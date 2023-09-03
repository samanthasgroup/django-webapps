from api.models import Student
from api.models.group import Group
from api.processors.actions import StudentTransferProcessor


class StudentProcessor:
    """A Facade class providing access to actions with students."""

    @staticmethod
    def transfer(student: Student, to_group: Group) -> None:
        StudentTransferProcessor(student, to_group).process()
