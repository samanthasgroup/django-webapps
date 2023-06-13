import datetime

from django.db import transaction
from django.utils import timezone

from api.models import CoordinatorLogEvent, Group, GroupLogEvent, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_types import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.statuses import (
    CoordinatorStatus,
    GroupStatus,
    StudentStatus,
    TeacherStatus,
)
from api.models.people import CoordinatorQuerySet, TeacherQuerySet
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

        for category in ("coordinators", "students", "teachers"):
            getattr(cls, f"_set_{category}_status_start")(group=group, timestamp=timestamp)

    @staticmethod
    def _set_coordinators_status_start(group: Group, timestamp: datetime.datetime) -> None:
        # the type is actually Manager, but we put QuerySet here to stop IDE and mypy
        # complaining about missing attributes (since we're using `as_manager()` in the model)
        coordinators: CoordinatorQuerySet = group.coordinators  # type: ignore[assignment]

        coordinators.below_threshold().update(
            status=CoordinatorStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.above_threshold_and_within_limit().update(
            status=CoordinatorStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.limit_reached().update(
            status=CoordinatorStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )

    @staticmethod
    def _set_students_status_start(group: Group, timestamp: datetime.datetime) -> None:
        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )

    @staticmethod
    def _set_teachers_status_start(group: Group, timestamp: datetime.datetime) -> None:
        # the type is actually Manager, but we put QuerySet here to stop IDE and mypy
        # complaining about missing attributes (since we're using `as_manager()` in the model)
        teachers: TeacherQuerySet = group.teachers  # type: ignore[assignment]

        teachers.can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=timestamp,
        )

        teachers.cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )
