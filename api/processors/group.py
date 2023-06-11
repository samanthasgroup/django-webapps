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
        cls._set_status(obj=group, status=GroupStatus.WORKING)

        # FIXME things below depend on teacher's/coordinator's params, just showing general logic

        for coordinator in group.coordinators.iterator():
            cls._set_status(obj=coordinator, status=CoordinatorStatus.WORKING_OK)

        for teacher in group.teachers.iterator():
            cls._set_status(obj=teacher, status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE)

        for student in group.students.iterator():
            cls._set_status(obj=student, status=StudentStatus.STUDYING)
