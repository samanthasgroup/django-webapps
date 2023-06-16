import datetime

from django.db import transaction
from django.utils import timezone

from api.models import (
    Coordinator,
    CoordinatorLogEvent,
    Group,
    GroupLogEvent,
    StudentLogEvent,
    Teacher,
    TeacherLogEvent,
)
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import CoordinatorStatus, GroupStatus, StudentStatus, TeacherStatus
from api.processors.base import Processor


class GroupProcessor(Processor):
    @classmethod
    @transaction.atomic
    def start(cls, group: Group) -> None:
        cls._create_log_events_start(group)
        cls._set_statuses_start(group)

    @classmethod
    def _create_log_events_start(cls, group: Group) -> None:
        GroupLogEvent.objects.create(group=group, type=GroupLogEventType.STARTED)

        CoordinatorLogEvent.objects.bulk_create(
            CoordinatorLogEvent(
                coordinator=coordinator,
                group=group,
                type=CoordinatorLogEventType.TOOK_NEW_GROUP,
            )
            for coordinator in group.coordinators.iterator()
        )

        StudentLogEvent.objects.bulk_create(
            StudentLogEvent(student=student, to_group=group, type=StudentLogEventType.STUDY_START)
            for student in group.students.iterator()
        )

        TeacherLogEvent.objects.bulk_create(
            TeacherLogEvent(teacher=teacher, to_group=group, type=TeacherLogEventType.STUDY_START)
            for teacher in group.teachers.iterator()
        )

    @classmethod
    def _set_statuses_start(cls, group: Group) -> None:
        timestamp = timezone.now()

        cls._set_status(obj=group, status=GroupStatus.WORKING, status_since=timestamp)

        cls._set_coordinators_status_start(timestamp)
        cls._set_students_status_start(group=group, timestamp=timestamp)
        cls._set_teachers_status_start(timestamp)

    @staticmethod
    def _set_coordinators_status_start(timestamp: datetime.datetime) -> None:
        coordinators = Coordinator.objects

        coordinators.filter_below_threshold().update(
            status=CoordinatorStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.filter_above_threshold_and_within_limit().update(
            status=CoordinatorStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.filter_limit_reached().update(
            status=CoordinatorStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )

    @staticmethod
    def _set_students_status_start(group: Group, timestamp: datetime.datetime) -> None:
        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )

    @staticmethod
    def _set_teachers_status_start(timestamp: datetime.datetime) -> None:
        teachers = Teacher.objects

        teachers.filter_can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=timestamp,
        )

        teachers.filter_cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )
