from django.db import transaction

from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import (
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import (
    GroupProjectStatus,
    StudentSituationalStatus,
    TeacherProjectStatus,
    TeacherSituationalStatus,
)
from api.processors.actions.group import GroupActionProcessor
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupCreateProcessor(GroupActionProcessor):
    @transaction.atomic
    def process(self) -> None:
        self._set_statuses()
        self._create_log_events()

    def _create_log_events(self) -> None:
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.GROUP_OFFERED,
            teacher_log_event_type=TeacherLogEventType.GROUP_OFFERED,
            group_log_event_type=GroupLogEventType.FORMED,
            to_group=self.group,
        )

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group, project_status=GroupProjectStatus.PENDING, status_since=self.timestamp
        )

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_teachers_status(self) -> None:
        self.group.teachers.all().filter_active().update(  # type: ignore[attr-defined]
            project_status=TeacherProjectStatus.WORKING,
            situational_status=TeacherSituationalStatus.GROUP_OFFERED,
            status_since=self.timestamp,
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            situational_status=StudentSituationalStatus.GROUP_OFFERED, status_since=self.timestamp
        )
