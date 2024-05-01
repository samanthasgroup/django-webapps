from django.db import transaction

from api.models import Group
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import StudentLogEventType, TeacherLogEventType
from api.models.choices.status import StudentProjectStatus, TeacherProjectStatus
from api.processors.actions.group import GroupActionProcessor
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupDiscardProcessor(GroupActionProcessor):
    def __init__(self, group: Group, reason: str):
        self.reason = reason
        super().__init__(group)

    @transaction.atomic
    def process(self) -> None:
        self._set_statuses()
        self._create_log_events()
        self._delete()

    def _create_log_events(self) -> None:
        # TODO add from_groupd once CASCAD policy removed
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.TENTATIVE_GROUP_DISCARDED,
            teacher_log_event_type=TeacherLogEventType.TENTATIVE_GROUP_DISCARDED,
            comment=self.reason,
        )

    def _delete(self) -> None:
        self.group.delete()

    def _set_group_status(self) -> None:
        pass

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_teachers_status(self) -> None:
        self.group.teachers_with_other_groups().update(
            project_status=TeacherProjectStatus.WORKING,
            situational_status="",
            status_since=self.timestamp,
        )

        self.group.teachers_with_no_other_groups().update(
            project_status=TeacherProjectStatus.NO_GROUP_YET,
            situational_status="",
            status_since=self.timestamp,
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            # TODO actually student can theoretically be studying in a different group already,
            #  so additional check will be needed instead of blindly setting NO_GROUP_YET.
            #  However, this definitely won't be the case in the MVP.
            project_status=StudentProjectStatus.NO_GROUP_YET,
            situational_status="",
            status_since=self.timestamp,
        )
