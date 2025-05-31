from alerts.handlers.coordinator import CoordinatorOverdueLeaveHandler
from alerts.handlers.teacher import TeacherNoGroup45DaysHandler

ALERT_HANDLERS = [
    CoordinatorOverdueLeaveHandler,
    TeacherNoGroup45DaysHandler,
]

__all__ = [
    "ALERT_HANDLERS",
    "CoordinatorOverdueLeaveHandler",
]
