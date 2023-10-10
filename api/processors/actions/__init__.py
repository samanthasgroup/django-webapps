from api.processors.actions.group.abort import GroupAbortProcessor
from api.processors.actions.group.create import GroupCreateProcessor
from api.processors.actions.group.discard import GroupDiscardProcessor
from api.processors.actions.group.finish import GroupFinishProcessor
from api.processors.actions.group.start import GroupStartProcessor
from api.processors.actions.student.finished_and_left import StudentFinishedAndLeftProcessor
from api.processors.actions.student.missed_class import StudentMissedClassProcessor
from api.processors.actions.student.put_on_wait import StudentPutOnWaitProcessor
from api.processors.actions.student.returned_from_leave import StudentReturnedFromLeaveProcessor
from api.processors.actions.student.transfer import StudentTransferProcessor
from api.processors.actions.student.went_on_leave import StudentWentOnLeaveProcessor
from api.processors.actions.teacher.returned_from_leave import TeacherReturnedFromLeaveProcessor
from api.processors.actions.teacher.transfer import TeacherTransferProcessor
from api.processors.actions.teacher.went_on_leave import TeacherWentOnLeaveProcessor

__all__ = [
    "GroupAbortProcessor",
    "GroupStartProcessor",
    "GroupCreateProcessor",
    "GroupDiscardProcessor",
    "GroupFinishProcessor",
    "StudentTransferProcessor",
    "StudentMissedClassProcessor",
    "TeacherTransferProcessor",
    "TeacherWentOnLeaveProcessor",
    "StudentWentOnLeaveProcessor",
    "TeacherReturnedFromLeaveProcessor",
    "StudentReturnedFromLeaveProcessor",
    "StudentPutOnWaitProcessor",
    "StudentFinishedAndLeftProcessor",
]
