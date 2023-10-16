from django.db import transaction

from api.models import Teacher
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.log_event import TeacherLogEvent
from api.processors.actions.teacher import TeacherActionProcessor


class TeacherLeftProjectPrematurelyProcessor(TeacherActionProcessor):
    def __init__(self, teacher: Teacher):
        super().__init__(teacher)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._update_groups()
        self._set_statuses()

    def _update_groups(self) -> None:
        for group in self.teacher.groups.all():
            group.teachers.remove(self.teacher)
            group.teachers_former.add(self.teacher)

    def _set_statuses(self) -> None:
        self.teacher.project_status = TeacherLogEventType.LEFT_PREMATURELY
        self.teacher.situational_status = ""
        self.teacher.status_since = self.timestamp
        self.teacher.save()

    def _create_log_events(self) -> None:
        TeacherLogEvent.objects.create(
            teacher=self.teacher, type=TeacherLogEventType.LEFT_PREMATURELY
        )
