from django.db import transaction

from api.models import Student
from api.models.choices.log_event_type import StudentLogEventType
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentCreateProcessor(StudentActionProcessor):
    def __init__(self, student: Student):
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()

    def _set_statuses(self) -> None:
        pass

    def _create_log_events(self) -> None:
        StudentLogEvent.objects.create(student=self.student, type=StudentLogEventType.REGISTERED)
        if self.student.teaching_languages_and_levels.exists():
            StudentLogEvent.objects.create(
                student=self.student, type=StudentLogEventType.AWAITING_OFFER
            )
