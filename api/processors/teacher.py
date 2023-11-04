from api.models import Teacher
from api.models.group import Group
from api.processors.actions import (
    TeacherCreateProcessor,
    TeacherExpelledProcessor,
    TeacherFinishedStudiesButStaysInProjectProcessor,
    TeacherLeftProjectPrematurelyProcessor,
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

    @staticmethod
    def left_project_prematurely(teacher: Teacher) -> None:
        TeacherLeftProjectPrematurelyProcessor(teacher).process()

    @staticmethod
    def expelled(teacher: Teacher) -> None:
        TeacherExpelledProcessor(teacher).process()

    @staticmethod
    def create(teacher: Teacher) -> None:
        TeacherCreateProcessor(teacher).process()

    @staticmethod
    def finished_but_stays_in_project(teacher: Teacher) -> None:
        TeacherFinishedStudiesButStaysInProjectProcessor(teacher).process()
