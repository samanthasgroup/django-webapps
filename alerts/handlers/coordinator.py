from alerts.config import AlertConfig
from alerts.handlers.date_threshold import DateThresholdHandler
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.models.coordinator import Coordinator


class CoordinatorOverdueLeaveHandler(DateThresholdHandler):
    """Координатор в отпуске дольше допустимого периода (2 недели)."""

    MODEL = Coordinator
    EVENT_MODEL = __import__(
        "api.models.log_event", fromlist=["CoordinatorLogEvent"]
    ).CoordinatorLogEvent
    EVENT_TYPE = CoordinatorLogEventType.GONE_ON_LEAVE
    STATUS_FIELD = "project_status"
    STATUS_VALUE = __import__(
        "api.models.choices.status.project", fromlist=["CoordinatorProjectStatus"]
    ).CoordinatorProjectStatus.ON_LEAVE
    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["OVERDUE_ON_LEAVE"]
