from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, ClassVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, QuerySet
from django.utils import timezone

from alerts.handlers.base import AlertHandler
from alerts.models import Alert

logger = logging.getLogger(__name__)


class StatusSinceHandler(AlertHandler):
    """
    Обработчик «статус + status_since + порог по времени».
    Необходимые атрибуты в подклассе:
      - MODEL: Django-модель, по которой создаются алерты
      - STATUS_FIELD: строка с именем поля статуса (на модели MODEL)
      - STATUS_VALUE: значение для STATUS_FIELD при активном алерте
      - PERIOD: datetime.timedelta — порог «старости» статуса
      - ALERT_TYPE: строковый тип алерта из AlertConfig.TYPES
    """

    MODEL: ClassVar[type[Model]]
    STATUS_FIELD: ClassVar[str]
    STATUS_VALUE: ClassVar[Any]
    PERIOD: ClassVar[timedelta]
    ALERT_TYPE: ClassVar[str]

    def __init__(self) -> None:
        assert self.MODEL and self.STATUS_FIELD and self.STATUS_VALUE is not None
        assert self.PERIOD and self.ALERT_TYPE
        ct = ContentType.objects.get_for_model(self.MODEL)
        super().__init__(ct, self.ALERT_TYPE)
        self.now = timezone.now()

    def _get_threshold_qs(self) -> QuerySet[Model]:
        threshold = self.now - self.PERIOD
        return self.MODEL.objects.filter(  # type: ignore[attr-defined]
            **{self.STATUS_FIELD: self.STATUS_VALUE, "status_since__lte": threshold}
        )

    def check_and_create_alerts(self, processed: dict[str, int]) -> None:
        qs = self._get_threshold_qs()
        overdue_rows = list(qs.values("pk", "status_since"))
        overdue_ids = {row["pk"] for row in overdue_rows}
        existing = set(
            Alert.objects.filter(
                content_type=self.content_type,
                object_id__in=overdue_ids,
                alert_type=self.alert_type,
                is_resolved=False,
            ).values_list("object_id", flat=True)
        )
        new_ids = overdue_ids - existing
        alerts = []
        for row in overdue_rows:
            pk = row["pk"]
            if pk not in new_ids:
                continue
            since = row["status_since"]
            if since is None:
                continue
            details = (
                f"{str(self.MODEL._meta.verbose_name).capitalize()} с ID={pk}: "
                f"статус {self.STATUS_VALUE} с {since.date()}; прошло {self.PERIOD.days} дней."
            )
            alerts.append(
                Alert(
                    content_type=self.content_type,
                    object_id=pk,
                    alert_type=self.alert_type,
                    details=details,
                )
            )
            logger.info(f"Created alert {self.ALERT_TYPE} for {self.MODEL.__name__} {pk}")
        self._bulk_create_alerts(alerts, processed)

    def resolve_alerts(self, processed: dict[str, int]) -> None:
        active = Alert.objects.filter(
            content_type=self.content_type,
            alert_type=self.alert_type,
            is_resolved=False,
        )
        to_resolve = []
        for alert in active:
            obj = self.MODEL.objects.filter(pk=alert.object_id).first()  # type: ignore[attr-defined]
            if not obj or getattr(obj, self.STATUS_FIELD) != self.STATUS_VALUE:
                to_resolve.append(alert.pk)
        if to_resolve:
            count = Alert.objects.filter(pk__in=to_resolve).update(is_resolved=True, resolved_at=self.now)
            processed["resolved"] += count
            logger.info(f"Resolved {count} {self.ALERT_TYPE} alerts.")
