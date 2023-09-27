from api.models import Teacher
from api.models.group import Group
from api.processors.actions import (
    TeacherReturnedFromLeaveProcessor,
    TeacherTransferProcessor,
    TeacherWentOnLeaveProcessor,
)


class TeacherProcessor:
    """A Facade class providing access to actions with teachers."""

    @staticmethod
    def transfer(teacher: Teacher, to_group: Group, from_group: Group) -> None:
        TeacherTransferProcessor(teacher, to_group, from_group).process()

    @staticmethod
    def went_on_leave(teacher: Teacher) -> None:
        TeacherWentOnLeaveProcessor(teacher).process()

    @staticmethod
    def returned_from_leave(teacher: Teacher) -> None:
        TeacherReturnedFromLeaveProcessor(teacher).process()
