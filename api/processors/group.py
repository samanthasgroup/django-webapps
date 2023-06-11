from datetime import datetime

import pytz

from api.models import Group
from api.models.choices.statuses import (
    CoordinatorStatus,
    GroupStatus,
    StudentStatus,
    TeacherStatus,
)
from api.processors.base import Processor


class GroupProcessor(Processor):
    @classmethod
    def start(cls, group: Group) -> None:
        timestamp = datetime.now(tz=pytz.UTC)

        cls._set_status(obj=group, status=GroupStatus.WORKING, status_since=timestamp)

        # FIXME set status depending on whether the threshold or limit is reached
        group.coordinators.update(status=CoordinatorStatus.WORKING_OK, status_since=timestamp)

        # FIXME set status depending on max_groups of teacher
        group.teachers.update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )

        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )
