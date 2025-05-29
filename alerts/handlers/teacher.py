from alerts.config import AlertConfig
from alerts.handlers.date_threshold import DateThresholdHandler
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.teacher import Teacher


class TeacherNoGroup45DaysHandler(DateThresholdHandler):
    MODEL = Teacher
    EVENT_MODEL = __import__("api.models.log_event", fromlist=["TeacherLogEvent"]).TeacherLogEvent
    EVENT_TYPE = TeacherLogEventType.AWAITING_OFFER

    STATUS_FIELD = "project_status"
    STATUS_VALUE = __import__(
        "api.models.choices.status", fromlist=["TeacherProjectStatus"]
    ).TeacherProjectStatus.NO_GROUP_YET

    PERIOD = AlertConfig.PERIODS["FORTY_FIVE_DAYS"]
    ALERT_TYPE = AlertConfig.TYPES["TEACHER_NO_GROUP_45_DAYS"]
