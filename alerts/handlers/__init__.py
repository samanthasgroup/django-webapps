from alerts.handlers.coordinator import CoordinatorOverdueLeaveHandler

ALERT_HANDLERS = [
    CoordinatorOverdueLeaveHandler,
]

__all__ = [
    "ALERT_HANDLERS",
    "CoordinatorOverdueLeaveHandler",
]
