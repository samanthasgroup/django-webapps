from django.db import transaction

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


class GroupAbortProcessor(GroupActionProcessor):
    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._move_related_people_to_former()
        self._set_statuses()

    def _create_log_events(self) -> None:
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.GROUP_ABORTED,
            teacher_log_event_type=TeacherLogEventType.GROUP_ABORTED,
            coordinator_log_event_type=CoordinatorLogEventType.GROUP_ABORTED,
            group_log_event_type=GroupLogEventType.ABORTED,
        )

    def _move_related_people_to_former(self) -> None:
        teachers_current, students_current, coordinators_current = (
            self.group.teachers,
            self.group.students,
            self.group.coordinators,
        )

        self.group.teachers.clear()
        self.group.students.clear()
        self.group.coordinators.clear()
        self.group.teachers_former.add(*teachers_current.all())
        self.group.students_former.add(*students_current.all())
        self.group.coordinators_former.add(*coordinators_current.all())
        self.group.save()

    def _set_coordinators_status(self) -> None:
        StatusSetter.set_coordinator_statuses(self.timestamp)

    def _set_group_status(self) -> None:
        StatusSetter.set_status(
            obj=self.group, status=GroupStatus.ABORTED, status_since=self.timestamp
        )

    def _set_teachers_status(self) -> None:
        teachers = Teacher.objects

        teachers.filter_has_no_groups().update(
            status=TeacherStatus.AWAITING_OFFER,
            status_since=self.timestamp,
        )

        teachers.filter_has_groups().filter_can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=self.timestamp,
        )

        teachers.filter_cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=self.timestamp,
        )

    def _set_students_status(self) -> None:
        self.group.students.update(
            status=StudentStatus.STUDYING,
            status_since=self.timestamp,
        )
