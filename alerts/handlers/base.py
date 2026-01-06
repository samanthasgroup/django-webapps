import logging
from abc import ABC, abstractmethod

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from alerts.models import Alert

logger = logging.getLogger(__name__)


class AlertHandler(ABC):
    """Базовый класс для обработчиков алертов."""

    def __init__(self, content_type: ContentType, alert_type: str):
        self.content_type = content_type
        self.alert_type = alert_type
        self.now = timezone.now()

    @abstractmethod
    def check_and_create_alerts(self, processed_alerts: dict[str, int]) -> None:
        """Проверяет условия и создает алерты."""
        pass

    @abstractmethod
    def resolve_alerts(self, processed_alerts: dict[str, int]) -> None:
        """Проверяет и разрешает существующие алерты."""
        pass

    def _bulk_create_alerts(self, alerts_to_create: list[Alert], processed_alerts: dict[str, int]) -> None:
        """Создает список алертов с обработкой ошибок."""
        if not alerts_to_create:
            return

        try:
            created_alerts = Alert.objects.bulk_create(alerts_to_create)
            logger.info(f"Created {len(created_alerts)} {self.alert_type} alerts.")
            processed_alerts["created"] += len(created_alerts)
        except Exception as e:
            logger.error(f"Error bulk creating {self.alert_type} alerts: {e}")
            # Резервная логика: попытаться создать по одному
            self._fallback_create_alerts(alerts_to_create, processed_alerts)

    def _fallback_create_alerts(self, alerts_to_create: list[Alert], processed_alerts: dict[str, int]) -> None:
        """Резервный метод создания алертов по одному в случае ошибки bulk_create."""
        created_count = 0
        for alert in alerts_to_create:
            try:
                alert.save()
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating single {self.alert_type} alert for object {alert.object_id}: {e}")

        processed_alerts["created"] += created_count
        if created_count > 0:
            logger.info(f"Created {created_count} {self.alert_type} alerts using fallback method.")
