import datetime

from django.db import transaction

from api.models import Group, Teacher
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import GroupStatus, StudentStatus, TeacherStatus
from api.processors.group.actions.base import (
    BaseActionProcessor,
    CommonCoordinatorsStatusSetter,
    CommonLogEventsCreator,
)


class AbortProcessor(BaseActionProcessor):
    @classmethod
    @transaction.atomic
    def process(cls, group: Group) -> None:
        cls._create_log_events(group)
        cls._move_related_people_to_former(group)
        cls._set_statuses(group, group_status=GroupStatus.ABORTED)

    @classmethod
    def _set_coordinators_status(cls, timestamp: datetime.datetime) -> None:
        CommonCoordinatorsStatusSetter.set(timestamp)

    @classmethod
    def _set_teachers_status(cls, timestamp: datetime.datetime) -> None:
        teachers = Teacher.objects

        teachers.filter_has_no_groups().update(
            status=TeacherStatus.AWAITING_OFFER,
            status_since=timestamp,
        )

        teachers.filter_has_groups().filter_can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=timestamp,
        )

        teachers.filter_cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )

    @classmethod
    def _set_students_status(cls, group: Group, timestamp: datetime.datetime) -> None:
        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )

    @classmethod
    def _create_log_events(cls, group: Group) -> None:
        CommonLogEventsCreator.create(
            group=group,
            student_log_event_type=StudentLogEventType.GROUP_ABORTED,
            teacher_log_event_type=TeacherLogEventType.GROUP_ABORTED,
            coordinator_log_event_type=CoordinatorLogEventType.GROUP_ABORTED,
            group_log_event_type=GroupLogEventType.ABORTED,
        )

    @classmethod
    def _move_related_people_to_former(cls, group: Group) -> None:
        teachers_current, students_current, coordinators_current = (
            group.teachers,
            group.students,
            group.coordinators,
        )

        group.teachers.clear()
        group.students.clear()
        group.coordinators.clear()
        group.teachers_former.add(*teachers_current.all())
        group.students_former.add(*students_current.all())
        group.coordinators_former.add(*coordinators_current.all())
        group.save()
