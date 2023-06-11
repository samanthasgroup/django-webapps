from datetime import datetime

import pytz

from api.models import Group
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
        timestamp = datetime.now(tz=pytz.UTC)

        cls._set_status(obj=group, status=GroupStatus.WORKING, status_since=timestamp)

        # cannot use "has_enough_groups" or "has_reached_group_limit" because they are properties
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

        # FIXME set status depending on max_groups of teacher
        group.teachers.update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )

        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )
