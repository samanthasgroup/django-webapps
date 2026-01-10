from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from alerts.config import AlertConfig
from alerts.handlers.base import AlertHandler
from alerts.handlers.date_threshold import DateThresholdHandler
from alerts.models import Alert
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.choices.status import TeacherProjectStatus
from api.models.log_event import TeacherLogEvent
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


class TeacherOverdueOnLeaveHandler(DateThresholdHandler):
    """Учитель в отпуске дольше допустимого периода (2 недели)."""

    MODEL = Teacher
    EVENT_MODEL = __import__("api.models.log_event", fromlist=["TeacherLogEvent"]).TeacherLogEvent
    EVENT_TYPE = TeacherLogEventType.GONE_ON_LEAVE

    STATUS_FIELD = "project_status"
    STATUS_VALUE = TeacherProjectStatus.ON_LEAVE

    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["TEACHER_OVERDUE_ON_LEAVE"]


class TeacherOverdueGroupOfferHandler(AlertHandler):
    """Учитель получил предложение группы и не ответил дольше 2 недель."""

    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["TEACHER_OVERDUE_GROUP_OFFER"]
    RESOLVE_TYPES = [
        TeacherLogEventType.ACCEPTED_OFFER,
        TeacherLogEventType.DECLINED_OFFER,
        TeacherLogEventType.GROUP_CONFIRMED,
        TeacherLogEventType.STUDY_START,
        TeacherLogEventType.TENTATIVE_GROUP_DISCARDED,
    ]

    def __init__(self) -> None:
        ct = ContentType.objects.get_for_model(Teacher)
        super().__init__(ct, self.ALERT_TYPE)
        self.now = timezone.now()

    def _get_overdue_offers(self) -> dict[int, TeacherLogEvent]:
        threshold = self.now - self.PERIOD
        offers = (
            TeacherLogEvent.objects.filter(type=TeacherLogEventType.GROUP_OFFERED)
            .select_related("teacher")
            .order_by("teacher_id", "-date_time")
        )
        latest_offers: dict[int, TeacherLogEvent] = {}
        seen_teachers: set[int] = set()
        for offer in offers:
            if offer.teacher_id in seen_teachers:
                continue
            seen_teachers.add(offer.teacher_id)
            if offer.teacher is None or offer.teacher.project_status != TeacherProjectStatus.NO_GROUP_YET:
                continue
            if offer.date_time > threshold:
                continue
            latest_offers[offer.teacher_id] = offer
        if not latest_offers:
            return {}

        overdue: dict[int, TeacherLogEvent] = {}
        for teacher_id, offer in latest_offers.items():
            has_response = TeacherLogEvent.objects.filter(
                teacher_id=teacher_id,
                type__in=self.RESOLVE_TYPES,
                date_time__gt=offer.date_time,
            ).exists()
            if not has_response:
                overdue[teacher_id] = offer
        return overdue

    def check_and_create_alerts(self, processed: dict[str, int]) -> None:
        overdue = self._get_overdue_offers()
        overdue_ids = set(overdue)
        if not overdue_ids:
            return

        existing = set(
            Alert.objects.filter(
                content_type=self.content_type,
                object_id__in=overdue_ids,
                alert_type=self.alert_type,
                is_resolved=False,
            ).values_list("object_id", flat=True)
        )
        new_ids = overdue_ids - existing
        alerts: list[Alert] = []
        for teacher_id in new_ids:
            offer = overdue[teacher_id]
            details = (
                f"Учитель с ID={teacher_id}: предложение группы от {offer.date_time.date()} "
                f"остается без ответа более {self.PERIOD.days} дней."
            )
            alerts.append(
                Alert(
                    content_type=self.content_type,
                    object_id=teacher_id,
                    alert_type=self.alert_type,
                    details=details,
                )
            )
        self._bulk_create_alerts(alerts, processed)

    def resolve_alerts(self, processed: dict[str, int]) -> None:
        overdue_ids = set(self._get_overdue_offers().keys())
        active = Alert.objects.filter(
            content_type=self.content_type,
            alert_type=self.alert_type,
            is_resolved=False,
        )
        to_resolve = [alert.pk for alert in active if alert.object_id not in overdue_ids]
        if to_resolve:
            count = Alert.objects.filter(pk__in=to_resolve).update(is_resolved=True, resolved_at=self.now)
            processed["resolved"] += count
