from django.db import transaction

from api.models import Group, Student
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status.situational import StudentSituationalStatus
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentOfferJoinGroupProcessor(StudentActionProcessor):
    def __init__(self, student: Student, to_group: Group):
        self.to_group = to_group
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._set_statuses()
        self._create_log_events()

    def _set_statuses(self) -> None:
        self.student.situational_status = StudentSituationalStatus.GROUP_OFFERED
        self.student.status_since = self.timestamp
        self.student.save()

    def _create_log_events(self) -> None:
        StudentLogEvent.objects.create(
            student=self.student,
            to_group=self.to_group,
            type=StudentLogEventType.GROUP_OFFERED,
        )
