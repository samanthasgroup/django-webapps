from alerts.handlers.coordinator import (
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
)
from alerts.handlers.group import GroupAwaitingStartOverdueHandler, GroupPendingOverdueHandler
from alerts.handlers.student import (
    StudentNeedsOralInterviewHandler,
    StudentNoGroup30DaysHandler,
    StudentOverdueGroupOfferHandler,
)
from alerts.handlers.teacher import (
    TeacherNoGroup45DaysHandler,
    TeacherOverdueGroupOfferHandler,
    TeacherOverdueOnLeaveHandler,
)

ALERT_HANDLERS = [
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
    GroupAwaitingStartOverdueHandler,
    GroupPendingOverdueHandler,
    StudentNeedsOralInterviewHandler,
    StudentNoGroup30DaysHandler,
    StudentOverdueGroupOfferHandler,
    TeacherNoGroup45DaysHandler,
    TeacherOverdueGroupOfferHandler,
    TeacherOverdueOnLeaveHandler,
]

__all__ = [
    "ALERT_HANDLERS",
    "CoordinatorOnboardingStaleHandler",
    "CoordinatorOverdueLeaveHandler",
    "CoordinatorOverdueTransferRequestHandler",
    "GroupAwaitingStartOverdueHandler",
    "GroupPendingOverdueHandler",
    "StudentNeedsOralInterviewHandler",
    "StudentNoGroup30DaysHandler",
    "StudentOverdueGroupOfferHandler",
    "TeacherNoGroup45DaysHandler",
    "TeacherOverdueGroupOfferHandler",
    "TeacherOverdueOnLeaveHandler",
]
