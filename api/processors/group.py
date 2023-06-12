import datetime

import pytz
from django.db.models import F

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
from api.models.constants import CoordinatorGroupLimit
from api.processors.base import Processor


class GroupProcessor(Processor):
    @classmethod
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
        timestamp = datetime.datetime.now(tz=pytz.UTC)

        cls._set_status(obj=group, status=GroupStatus.WORKING, status_since=timestamp)

        # Resulting status of coordinator depends on how many groups they now have.
        # We can't use "has_enough_groups" or "has_reached_group_limit" because they are properties
        group.coordinators.filter(groups__count_lt=CoordinatorGroupLimit.MIN).update(
            status=CoordinatorStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )

        group.coordinators.filter(
            groups__count__gte=CoordinatorGroupLimit.MIN,
            groups__count__lt=CoordinatorGroupLimit.MAX,
        ).update(status=CoordinatorStatus.WORKING_OK, status_since=timestamp)

        group.coordinators.filter(groups__count__gte=CoordinatorGroupLimit.MAX).update(
            status=CoordinatorStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )

        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )

        group.teachers.filter(groups__count__lt=F("simultaneous_groups")).update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=timestamp,
        )

        group.teachers.filter(groups__count__gte=F("simultaneous_groups")).update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )
