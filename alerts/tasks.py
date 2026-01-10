import logging

from celery import shared_task

from alerts.handlers import ALERT_HANDLERS
from alerts.models import Alert

logger = logging.getLogger(__name__)


@shared_task(name="alerts.tasks.check_system_alerts")  # type: ignore[misc]
def check_system_alerts() -> str:
    """
    Периодически проверяет условия для разных моделей и создает/разрешает алерты
    используя GenericForeignKey.
    """
    processed_alerts = {"created": 0, "resolved": 0}

    # Инициализация и запуск всех обработчиков алертов
    for handler_class in ALERT_HANDLERS:
        try:
            handler = handler_class()  # type: ignore[abstract]
            handler.check_and_create_alerts(processed_alerts)
            handler.resolve_alerts(processed_alerts)
        except Exception:
            logger.exception("Error processing alerts with handler %s", handler_class.__name__)

    logger.info(
        f"Alert check complete. Created: {processed_alerts['created']}. Resolved: {processed_alerts['resolved']}."
    )
    return f"Alert check complete. Created: {processed_alerts['created']}. Resolved: {processed_alerts['resolved']}."


@shared_task(name="alerts.tasks.create_demo_alerts")  # type: ignore[misc]
def create_demo_alerts(alert_specs: list[dict[str, str | int]]) -> int:
    created = 0
    for spec in alert_specs:
        try:
            alert = Alert.objects.create(
                alert_type=str(spec["alert_type"]),
                content_type_id=int(spec["content_type_id"]),
                object_id=int(spec["object_id"]),
                details=str(spec.get("details", "")),
            )
            logger.info(
                "Created demo alert %s for content_type=%s object_id=%s",
                alert.pk,
                alert.content_type_id,
                alert.object_id,
            )
            created += 1
        except Exception:
            logger.exception("Failed to create demo alert for spec=%s", spec)
    return created
