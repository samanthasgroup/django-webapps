import logging

from celery import shared_task

from alerts.handlers import ALERT_HANDLERS

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
            handler = handler_class()
            handler.check_and_create_alerts(processed_alerts)
            handler.resolve_alerts(processed_alerts)
        except Exception as e:
            logger.error(f"Error processing alerts with handler {handler_class.__name__}: {e}")

    logger.info(
        f"Alert check complete. Created: {processed_alerts['created']}. Resolved: {processed_alerts['resolved']}."
    )
    return f"Alert check complete. Created: {processed_alerts['created']}. Resolved: {processed_alerts['resolved']}."
