from django.db import transaction

from api.models import Group, Teacher
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.choices.status.project import TeacherProjectStatus
from api.models.log_event import TeacherLogEvent
from api.processors.actions.teacher import TeacherActionProcessor


class TeacherTransferProcessor(TeacherActionProcessor):
    def __init__(self, teacher: Teacher, to_group: Group, from_group: Group):
        self.to_group = to_group
        self.from_group = from_group
        super().__init__(teacher)

    @transaction.atomic
    def process(self) -> None:
        self._transfer()
        self._set_statuses()
        self._create_log_events()

    def _transfer(self) -> None:
        self.teacher.groups.remove(self.from_group)
        self.from_group.teachers_former.add(self.teacher)
        self.to_group.teachers.add(self.teacher)

    def _set_statuses(self) -> None:
        self.teacher.project_status = TeacherProjectStatus.WORKING
        self.teacher.situational_status = ""
        self.teacher.status_since = self.timestamp
        self.teacher.save()

    def _create_log_events(self) -> None:
        TeacherLogEvent.objects.create(
            teacher=self.teacher,
            from_group=self.from_group,
            to_group=self.to_group,
            type=TeacherLogEventType.TRANSFERRED,
        )
