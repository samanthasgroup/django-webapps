from api.processors.actions.coordinator.create import CoordinatorCreateProcessor
from api.processors.actions.group.abort import GroupAbortProcessor
from api.processors.actions.group.create import GroupCreateProcessor
from api.processors.actions.group.discard import GroupDiscardProcessor
from api.processors.actions.group.finish import GroupFinishProcessor
from api.processors.actions.group.start import GroupStartProcessor
from api.processors.actions.student.accepted_offered_group import (
    StudentAcceptedOfferedGroupProcessor,
)
from api.processors.actions.student.completed_oral_interview import (
    StudentCompletedOralInterviewProcessor,
)
from api.processors.actions.student.create import StudentCreateProcessor
from api.processors.actions.student.expelled import StudentExpelledProcessor
from api.processors.actions.student.finished_and_left import StudentFinishedAndLeftProcessor
from api.processors.actions.student.left_project_prematurely import (
    StudentLeftProjectPrematurelyProcessor,
)
from api.processors.actions.student.missed_class import StudentMissedClassProcessor
from api.processors.actions.student.offer_join_group import StudentOfferJoinGroupProcessor
from api.processors.actions.student.put_in_waiting_queue import StudentPutInWaitingQueueProcessor
from api.processors.actions.student.returned_from_leave import StudentReturnedFromLeaveProcessor
from api.processors.actions.student.transfer import StudentTransferProcessor
from api.processors.actions.student.went_on_leave import StudentWentOnLeaveProcessor
from api.processors.actions.teacher.create import TeacherCreateProcessor
from api.processors.actions.teacher.expelled import TeacherExpelledProcessor
from api.processors.actions.teacher.left_project_prematurely import (
    TeacherLeftProjectPrematurelyProcessor,
)
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
    "StudentPutInWaitingQueueProcessor",
    "StudentFinishedAndLeftProcessor",
    "StudentAcceptedOfferedGroupProcessor",
    "StudentOfferJoinGroupProcessor",
    "StudentLeftProjectPrematurelyProcessor",
    "TeacherLeftProjectPrematurelyProcessor",
    "StudentExpelledProcessor",
    "TeacherExpelledProcessor",
    "StudentCompletedOralInterviewProcessor",
    "CoordinatorCreateProcessor",
    "StudentCreateProcessor",
    "TeacherCreateProcessor",
]
