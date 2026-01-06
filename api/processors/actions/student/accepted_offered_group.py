from django.db import transaction

from api.models import Coordinator, Group, Student
from api.models.choices.log_event_type import CoordinatorLogEventType, StudentLogEventType
from api.models.choices.status import StudentProjectStatus
from api.models.log_event import CoordinatorLogEvent, StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentAcceptedOfferedGroupProcessor(StudentActionProcessor):
    """Student accepted offer to join group"""

    def __init__(self, student: Student, coordinator: Coordinator, group: Group):
        self.coordinator = coordinator
        self.group = group
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._set_statuses()

    def _set_statuses(self) -> None:
        self.student.project_status = StudentProjectStatus.STUDYING
        self.student.situational_status = ""
        self.student.status_since = self.timestamp
        self.student.save()

    def _create_log_events(self) -> None:
        StudentLogEvent.objects.create(student=self.student, to_group=self.group, type=StudentLogEventType.STUDY_START)
        CoordinatorLogEvent.objects.create(
            coordinator=self.coordinator,
            group=self.group,
            type=CoordinatorLogEventType.ADDED_STUDENT_TO_EXISTING_GROUP,
        )
