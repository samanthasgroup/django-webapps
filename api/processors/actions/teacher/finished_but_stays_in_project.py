from django.db import transaction

from api.models import Teacher
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.choices.status.project import TeacherProjectStatus
from api.models.log_event import TeacherLogEvent
from api.processors.actions.teacher import TeacherActionProcessor


class TeacherFinishedStudiesButStaysInProjectProcessor(TeacherActionProcessor):
    def __init__(self, teacher: Teacher):
        super().__init__(teacher)

    @transaction.atomic
    def process(self) -> None:
        self._check_groups()
        self._create_log_events()
        self._set_statuses()

    def _check_groups(self) -> None:
        if self.teacher.has_groups:
            raise ValueError("Unable to process teacher with groups")

    def _set_statuses(self) -> None:
        self.teacher.project_status = TeacherProjectStatus.FINISHED_STAYS
        self.teacher.status_since = self.timestamp
        self.teacher.save()

    def _create_log_events(self) -> None:
        TeacherLogEvent.objects.create(teacher=self.teacher, type=TeacherLogEventType.FINISHED_AND_STAYING)
