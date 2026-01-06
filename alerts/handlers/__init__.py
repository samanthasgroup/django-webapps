from alerts.handlers.coordinator import (
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
)
from alerts.handlers.teacher import TeacherNoGroup45DaysHandler

ALERT_HANDLERS = [
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
    TeacherNoGroup45DaysHandler,
]

__all__ = [
    "ALERT_HANDLERS",
    "CoordinatorOnboardingStaleHandler",
    "CoordinatorOverdueLeaveHandler",
    "CoordinatorOverdueTransferRequestHandler",
]
