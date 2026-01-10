from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from alerts.config import AlertConfig
from alerts.handlers.base import AlertHandler
from alerts.handlers.date_threshold import DateThresholdHandler
from alerts.handlers.status_since import StatusSinceHandler
from alerts.models import Alert
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status import StudentProjectStatus
from api.models.log_event import StudentLogEvent
from api.models.student import Student


class StudentNeedsOralInterviewHandler(StatusSinceHandler):
    """Ученик ожидает устного интервью дольше 2 недель."""

    MODEL = Student
    STATUS_FIELD = "project_status"
    STATUS_VALUE = StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL
    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["STUDENT_NEEDS_ORAL_INTERVIEW"]


class StudentNoGroup30DaysHandler(DateThresholdHandler):
    """Ученик ожидает группу дольше 30 дней."""

    MODEL = Student
    EVENT_MODEL = __import__("api.models.log_event", fromlist=["StudentLogEvent"]).StudentLogEvent
    EVENT_TYPE = StudentLogEventType.AWAITING_OFFER

    STATUS_FIELD = "project_status"
    STATUS_VALUE = StudentProjectStatus.NO_GROUP_YET

    PERIOD = AlertConfig.PERIODS["ONE_MONTH"]
    ALERT_TYPE = AlertConfig.TYPES["STUDENT_NO_GROUP_30_DAYS"]


class StudentOverdueGroupOfferHandler(AlertHandler):
    """Ученик получил предложение группы и не ответил дольше 2 недель."""

    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["STUDENT_OVERDUE_GROUP_OFFER"]
    RESOLVE_TYPES = [
        StudentLogEventType.ACCEPTED_OFFER,
        StudentLogEventType.DECLINED_OFFER,
        StudentLogEventType.GROUP_CONFIRMED,
        StudentLogEventType.STUDY_START,
        StudentLogEventType.TENTATIVE_GROUP_DISCARDED,
    ]

    def __init__(self) -> None:
        ct = ContentType.objects.get_for_model(Student)
        super().__init__(ct, self.ALERT_TYPE)
        self.now = timezone.now()

    def _get_overdue_offers(self) -> dict[int, StudentLogEvent]:
        threshold = self.now - self.PERIOD
        offers = (
            StudentLogEvent.objects.filter(type=StudentLogEventType.GROUP_OFFERED)
            .select_related("student")
            .order_by("student_id", "-date_time")
        )
        latest_offers: dict[int, StudentLogEvent] = {}
        seen_students: set[int] = set()
        for offer in offers:
            if offer.student_id in seen_students:
                continue
            seen_students.add(offer.student_id)
            if offer.student is None or offer.student.project_status != StudentProjectStatus.NO_GROUP_YET:
                continue
            if offer.date_time > threshold:
                continue
            latest_offers[offer.student_id] = offer
        if not latest_offers:
            return {}

        overdue: dict[int, StudentLogEvent] = {}
        for student_id, offer in latest_offers.items():
            has_response = StudentLogEvent.objects.filter(
                student_id=student_id,
                type__in=self.RESOLVE_TYPES,
                date_time__gt=offer.date_time,
            ).exists()
            if not has_response:
                overdue[student_id] = offer
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
        for student_id in new_ids:
            offer = overdue[student_id]
            details = (
                f"Ученик с ID={student_id}: предложение группы от {offer.date_time.date()} "
                f"остается без ответа более {self.PERIOD.days} дней."
            )
            alerts.append(
                Alert(
                    content_type=self.content_type,
                    object_id=student_id,
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
