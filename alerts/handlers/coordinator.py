from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.utils import timezone

from alerts.config import AlertConfig
from alerts.handlers.base import AlertHandler
from alerts.handlers.date_threshold import DateThresholdHandler
from alerts.models import Alert
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.models.choices.status.situational import CoordinatorSituationalStatus
from api.models.coordinator import Coordinator
from api.models.log_event import CoordinatorLogEvent


class CoordinatorOverdueLeaveHandler(DateThresholdHandler):
    """Координатор в отпуске дольше допустимого периода (2 недели)."""

    MODEL = Coordinator
    EVENT_MODEL = __import__("api.models.log_event", fromlist=["CoordinatorLogEvent"]).CoordinatorLogEvent
    EVENT_TYPE = CoordinatorLogEventType.GONE_ON_LEAVE
    STATUS_FIELD = "project_status"
    STATUS_VALUE = __import__(
        "api.models.choices.status.project", fromlist=["CoordinatorProjectStatus"]
    ).CoordinatorProjectStatus.ON_LEAVE
    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["OVERDUE_ON_LEAVE"]


class CoordinatorOverdueTransferRequestHandler(AlertHandler):
    """Координатор запросил перевод группы и это тянется дольше 2 недель."""

    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["OVERDUE_TRANSFER_REQUEST"]
    REQUEST_TYPE = CoordinatorLogEventType.REQUESTED_TRANSFER
    RESOLVE_TYPES = [
        CoordinatorLogEventType.TRANSFER_CANCELED,
        CoordinatorLogEventType.TRANSFER_COMPLETED,
    ]

    def __init__(self) -> None:
        ct = ContentType.objects.get_for_model(Coordinator)
        super().__init__(ct, self.ALERT_TYPE)
        self.now = timezone.now()

    def _get_overdue_requests(self) -> dict[int, list[CoordinatorLogEvent]]:
        threshold = self.now - self.PERIOD
        requests = (
            CoordinatorLogEvent.objects.filter(type=self.REQUEST_TYPE, date_time__lte=threshold)
            .select_related("coordinator", "group")
            .order_by("coordinator_id", "date_time")
        )
        overdue: dict[int, list[CoordinatorLogEvent]] = defaultdict(list)
        for request in requests:
            if request.group_id is None:
                continue
            has_resolve = CoordinatorLogEvent.objects.filter(
                coordinator_id=request.coordinator_id,
                group_id=request.group_id,
                type__in=self.RESOLVE_TYPES,
                date_time__gt=request.date_time,
            ).exists()
            if not has_resolve:
                overdue[request.coordinator_id].append(request)
        return overdue

    def check_and_create_alerts(self, processed: dict[str, int]) -> None:
        overdue = self._get_overdue_requests()
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
        for coordinator_id in new_ids:
            items = overdue[coordinator_id]
            details_items = ", ".join(f"группа {item.group_id} (запрос {item.date_time.date()})" for item in items)
            details = (
                f"Координатор с ID={coordinator_id}: запрос перевода "
                f"старше {self.PERIOD.days} дней. {details_items}."
            )
            alerts.append(
                Alert(
                    content_type=self.content_type,
                    object_id=coordinator_id,
                    alert_type=self.alert_type,
                    details=details,
                )
            )
        self._bulk_create_alerts(alerts, processed)

    def resolve_alerts(self, processed: dict[str, int]) -> None:
        overdue_ids = set(self._get_overdue_requests().keys())
        active = Alert.objects.filter(
            content_type=self.content_type,
            alert_type=self.alert_type,
            is_resolved=False,
        )
        to_resolve = [alert.pk for alert in active if alert.object_id not in overdue_ids]
        if to_resolve:
            count = Alert.objects.filter(pk__in=to_resolve).update(is_resolved=True, resolved_at=self.now)
            processed["resolved"] += count


class CoordinatorOnboardingStaleHandler(AlertHandler):
    """Координатор в онбординге слишком долго -> переводим в STALE и создаем алерт."""

    PERIOD = AlertConfig.PERIODS["TWO_WEEKS"]
    ALERT_TYPE = AlertConfig.TYPES["ONBOARDING_STALE"]
    ONBOARDING_STATUS = CoordinatorSituationalStatus.ONBOARDING
    STALE_STATUS = CoordinatorSituationalStatus.STALE

    def __init__(self) -> None:
        ct = ContentType.objects.get_for_model(Coordinator)
        super().__init__(ct, self.ALERT_TYPE)
        self.now = timezone.now()

    def _get_overdue_qs(self) -> QuerySet[Any]:
        threshold = self.now - self.PERIOD
        return Coordinator.objects.filter(situational_status=self.ONBOARDING_STATUS, status_since__lte=threshold)

    def check_and_create_alerts(self, processed: dict[str, int]) -> None:
        overdue_rows = list(self._get_overdue_qs().values("pk", "status_since"))
        if not overdue_rows:
            return

        overdue_ids = {row["pk"] for row in overdue_rows}
        Coordinator.objects.filter(pk__in=overdue_ids).update(
            situational_status=self.STALE_STATUS, status_since=self.now
        )

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
        for row in overdue_rows:
            coordinator_id = row["pk"]
            if coordinator_id not in new_ids:
                continue
            since = row["status_since"].date()
            details = f"Координатор с ID={coordinator_id}: онбординг старше {self.PERIOD.days} дней (c {since})."
            alerts.append(
                Alert(
                    content_type=self.content_type,
                    object_id=coordinator_id,
                    alert_type=self.alert_type,
                    details=details,
                )
            )
        self._bulk_create_alerts(alerts, processed)

    def resolve_alerts(self, processed: dict[str, int]) -> None:
        active = Alert.objects.filter(
            content_type=self.content_type,
            alert_type=self.alert_type,
            is_resolved=False,
        )
        to_resolve = []
        for alert in active:
            coordinator = Coordinator.objects.filter(pk=alert.object_id).first()
            if not coordinator or coordinator.situational_status != self.STALE_STATUS:
                to_resolve.append(alert.pk)
        if to_resolve:
            count = Alert.objects.filter(pk__in=to_resolve).update(is_resolved=True, resolved_at=self.now)
            processed["resolved"] += count
