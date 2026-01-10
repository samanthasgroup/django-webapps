import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.utils import timezone

from alerts.models import Alert

logger = logging.getLogger(__name__)


def create_alert_for_object(
    obj: Model, alert_type: str, details: str, content_type: None | ContentType = None
) -> None | Alert:
    """
    Создает алерт для конкретного объекта, если такого алерта еще нет.

    Args:
        obj: Объект модели, для которого создается алерт
        alert_type: Тип алерта
        details: Детали алерта
        content_type: ContentType объекта (если не указан, будет определен автоматически)

    Returns:
        Alert: Созданный алерт или None, если создание не удалось
    """
    if content_type is None:
        content_type = ContentType.objects.get_for_model(obj.__class__)

    # Проверяем, существует ли уже такой алерт
    existing_alert = Alert.objects.filter(
        content_type=content_type, object_id=obj.pk, alert_type=alert_type, is_resolved=False
    ).first()

    if existing_alert:
        logger.debug(f"Alert {alert_type} for {obj.__class__.__name__} #{obj.pk} already exists")
        return existing_alert

    try:
        alert = Alert.objects.create(
            content_type=content_type, object_id=obj.pk, alert_type=alert_type, details=details
        )
        logger.debug(f"Created alert {alert_type} for {obj.__class__.__name__} #{obj.pk}")
        return alert
    except Exception as e:
        logger.error(f"Error creating alert for {obj.__class__.__name__} #{obj.pk}: {e}")
        return None


def resolve_alerts_for_objects(model_class: type[Model], object_ids: list[int], alert_type: str) -> int:
    """
    Разрешает все активные алерты определенного типа для объектов.

    Args:
        model_class: Класс модели объектов
        object_ids: Список ID объектов
        alert_type: Тип алерта для разрешения

    Returns:
        int: Количество разрешенных алертов
    """
    if not object_ids:
        return 0

    content_type = ContentType.objects.get_for_model(model_class)

    try:
        return Alert.objects.filter(
            content_type=content_type,
            object_id__in=object_ids,
            alert_type=alert_type,
            is_resolved=False,
        ).update(is_resolved=True, resolved_at=timezone.now())
    except Exception as e:
        logger.error(f"Error resolving alerts for {model_class.__name__} objects: {e}")
        return 0
