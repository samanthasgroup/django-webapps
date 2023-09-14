from django.db import transaction
from django.db.models import Count

from api.models import Student
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


class GroupFinishProcessor(GroupActionProcessor):
    @transaction.atomic
    def process(self) -> None:
        self._set_statuses()
        self._create_log_events()
        self._move_related_people_to_former()

    def _create_log_events(self) -> None:
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.GROUP_FINISHED,
            teacher_log_event_type=TeacherLogEventType.GROUP_FINISHED,
            coordinator_log_event_type=CoordinatorLogEventType.GROUP_FINISHED,
            group_log_event_type=GroupLogEventType.FINISHED,
            from_group=self.group,
        )

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group, project_status=GroupProjectStatus.FINISHED, status_since=self.timestamp
        )

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
        annotated_students = Student.objects.annotate(groups_count=Count("groups")).filter(
            groups=self.group
        )

        # TODO: We should check group status or something
        #  to set correct status, not just count of groups
        #  Because other groups also could be finished etc.
        #  Maybe just don't change status for such students?
        annotated_students.filter(groups_count__gt=1).update(
            project_status=StudentProjectStatus.STUDYING,
            situational_status="",
            status_since=self.timestamp,
        )

        annotated_students.filter(groups_count=1).update(
            project_status=StudentProjectStatus.AWAITING_DECISION,
            situational_status="",
            status_since=self.timestamp,
        )
