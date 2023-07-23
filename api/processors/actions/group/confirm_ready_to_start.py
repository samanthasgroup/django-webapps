from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import GroupStatus, StudentStatus, TeacherStatus
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
        # status will change when the group starts studies
        pass

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group, status=GroupStatus.AWAITING_START, status_since=self.timestamp
        )

    def _set_teachers_status(self) -> None:
        self.group.teachers.update(
            status=TeacherStatus.AWAITING_START, status_since=self.timestamp
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            status=StudentStatus.AWAITING_START,
            status_since=self.timestamp,
        )
