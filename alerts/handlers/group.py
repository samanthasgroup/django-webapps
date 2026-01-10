from alerts.config import AlertConfig
from alerts.handlers.status_since import StatusSinceHandler
from api.models.choices.status import GroupProjectStatus
from api.models.group import Group


class GroupAwaitingStartOverdueHandler(StatusSinceHandler):
    """Группа подтверждена, но занятия не стартовали дольше 2 недель."""

    MODEL = Group
    STATUS_FIELD = "project_status"
    STATUS_VALUE = GroupProjectStatus.AWAITING_START
    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["GROUP_AWAITING_START_OVERDUE"]


class GroupPendingOverdueHandler(StatusSinceHandler):
    """Группа в статусе pending дольше 2 недель."""

    MODEL = Group
    STATUS_FIELD = "project_status"
    STATUS_VALUE = GroupProjectStatus.PENDING
    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["GROUP_PENDING_OVERDUE"]
