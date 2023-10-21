from api.models import Coordinator, Group, Student
from api.processors.actions import (
    StudentAcceptedOfferedGroupProcessor,
    StudentExpelledProcessor,
    StudentFinishedAndLeftProcessor,
    StudentLeftProjectPrematurelyProcessor,
    StudentMissedClassProcessor,
    StudentOfferJoinGroupProcessor,
    StudentPutInWaitingQueueProcessor,
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
    def put_in_waiting_queue(student: Student) -> None:
        StudentPutInWaitingQueueProcessor(student).process()

    @staticmethod
    def accepted_offered_group(student: Student, coordinator: Coordinator, group: Group) -> None:
        StudentAcceptedOfferedGroupProcessor(student, coordinator, group).process()

    @staticmethod
    def offer_join_group(student: Student, group: Group) -> None:
        StudentOfferJoinGroupProcessor(student, group).process()

    @staticmethod
    def left_project_prematurely(student: Student) -> None:
        StudentLeftProjectPrematurelyProcessor(student).process()

    @staticmethod
    def expelled(student: Student) -> None:
        StudentExpelledProcessor(student).process()
