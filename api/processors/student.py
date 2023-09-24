from api.models import Student
from api.models.group import Group
from api.processors.actions import (
    StudentMissedClassProcessor,
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
