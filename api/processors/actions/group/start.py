from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import (
    GroupProjectStatus,
    StudentProjectStatus,
    TeacherProjectStatus,
)
from api.processors.actions.group import GroupActionProcessor
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupStartProcessor(GroupActionProcessor):
    def _create_log_events(self) -> None:
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.STUDY_START,
            teacher_log_event_type=TeacherLogEventType.STUDY_START,
            coordinator_log_event_type=CoordinatorLogEventType.TOOK_NEW_GROUP,
            group_log_event_type=GroupLogEventType.STARTED,
        )

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group, project_status=GroupProjectStatus.WORKING, status_since=self.timestamp
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            project_status=StudentProjectStatus.STUDYING,
            situational_status="",
            status_since=self.timestamp,
        )

    def _set_teachers_status(self) -> None:
        self.group.teachers.all().filter_active().update(  # type: ignore[attr-defined]
            project_status=TeacherProjectStatus.WORKING,
            situational_status="",
            status_since=self.timestamp,
        )
