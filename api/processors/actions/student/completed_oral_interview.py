from django.db import transaction

from api.models import Student
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status.project import StudentProjectStatus
from api.models.language_and_level import LanguageAndLevel
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentCompletedOralInterviewProcessor(StudentActionProcessor):
    def __init__(self, student: Student, language_and_level: LanguageAndLevel):
        self.student = student
        self.language_and_level = language_and_level
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._add_language_and_level()
        self._set_statuses()
        self._create_log_events()

    def _add_language_and_level(self) -> None:
        self.student.teaching_languages_and_levels.add(self.language_and_level)

    def _set_statuses(self) -> None:
        self.student.project_status = StudentProjectStatus.NO_GROUP_YET
        self.student.situational_status = ""
        self.student.status_since = self.timestamp
        self.student.save()

    def _create_log_events(self) -> None:
        StudentLogEvent.objects.create(
            student=self.student,
            type=StudentLogEventType.AWAITING_OFFER,
        )
