from django.db import transaction

from api.models import Student
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status import StudentProjectStatus
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentLeftProjectPrematurelyProcessor(StudentActionProcessor):
    def __init__(self, student: Student):
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._update_groups()
        self._set_statuses()

    def _update_groups(self) -> None:
        for group in self.student.groups.all():
            group.students.remove(self.student)
            group.students_former.add(self.student)

    def _set_statuses(self) -> None:
        self.student.project_status = StudentProjectStatus.LEFT_PREMATURELY
        self.student.situational_status = ""
        self.student.status_since = self.timestamp
        self.student.save()

    def _create_log_events(self) -> None:
        StudentLogEvent.objects.create(
            student=self.student, type=StudentLogEventType.LEFT_PREMATURELY
        )
