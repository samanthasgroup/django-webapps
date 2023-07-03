from api.models import Teacher
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
            obj=self.group, status=GroupStatus.WORKING, status_since=self.timestamp
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            status=StudentStatus.STUDYING,
            status_since=self.timestamp,
        )

    def _set_teachers_status(self) -> None:
        teachers = Teacher.objects

        teachers.filter_can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=self.timestamp,
        )

        teachers.filter_cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=self.timestamp,
        )
