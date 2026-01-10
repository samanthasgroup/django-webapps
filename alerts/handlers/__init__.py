from alerts.handlers.coordinator import (
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
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
    TeacherNoGroup45DaysHandler,
    TeacherOverdueGroupOfferHandler,
    TeacherOverdueOnLeaveHandler,
]

__all__ = [
    "ALERT_HANDLERS",
    "CoordinatorOnboardingStaleHandler",
    "CoordinatorOverdueLeaveHandler",
    "CoordinatorOverdueTransferRequestHandler",
    "TeacherNoGroup45DaysHandler",
    "TeacherOverdueGroupOfferHandler",
    "TeacherOverdueOnLeaveHandler",
]
