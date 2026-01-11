from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import GroupProjectStatus
from api.processors.actions.group import GroupActionProcessor
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupConfirmReadyToStartProcessor(GroupActionProcessor):
    def _create_log_events(self) -> None:
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.GROUP_CONFIRMED,
            teacher_log_event_type=TeacherLogEventType.GROUP_CONFIRMED,
            coordinator_log_event_type=CoordinatorLogEventType.TOOK_NEW_GROUP,
            group_log_event_type=GroupLogEventType.CONFIRMED,
        )

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group,
            project_status=GroupProjectStatus.AWAITING_START,
            status_since=self.timestamp,
        )

    def _set_teachers_status(self) -> None:
        pass

    def _set_students_status(self) -> None:
        pass
