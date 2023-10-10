from api.models import Student
from api.models.group import Group
from api.processors.actions import (
    StudentFinishedAndLeftProcessor,
    StudentMissedClassProcessor,
    StudentPutOnWaitProcessor,
    StudentReturnedFromLeaveProcessor,
    StudentTransferProcessor,
    StudentWentOnLeaveProcessor,
)


class StudentProcessor:
    """A Facade class providing access to actions with students."""

    @staticmethod
    def transfer(student: Student, to_group: Group, from_group: Group) -> None:
        StudentTransferProcessor(student, to_group, from_group).process()

    @staticmethod
    def missed_class(student: Student, group: Group, notified: bool) -> None:
        StudentMissedClassProcessor(student, group, notified).process()

    @staticmethod
    def went_on_leave(student: Student) -> None:
        StudentWentOnLeaveProcessor(student).process()

    @staticmethod
    def returned_from_leave(student: Student) -> None:
        StudentReturnedFromLeaveProcessor(student).process()

    @staticmethod
    def finished_and_left(student: Student) -> None:
        StudentFinishedAndLeftProcessor(student).process()

    @staticmethod
    def put_on_wait(student: Student) -> None:
        StudentPutOnWaitProcessor(student).process()
