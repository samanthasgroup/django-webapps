import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Subquery

from alerts.config import AlertConfig
from alerts.handlers.base import AlertHandler
from alerts.models import Alert
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.models.choices.status.project import CoordinatorProjectStatus
from api.models.coordinator import Coordinator
from api.models.log_event import CoordinatorLogEvent

logger = logging.getLogger(__name__)


class CoordinatorOverdueLeaveHandler(AlertHandler):
    """Обработчик алертов для координаторов с просроченным отпуском."""

    def __init__(self) -> None:
        super().__init__(
            ContentType.objects.get_for_model(Coordinator), AlertConfig.TYPES["OVERDUE_ON_LEAVE"]
        )
        self.overdue_period = AlertConfig.PERIODS["TWO_WEEKS"]
        self.leave_event_type = CoordinatorLogEventType.GONE_ON_LEAVE

    def check_and_create_alerts(self, processed_alerts: dict[str, int]) -> None:
        """Проверяет координаторов с просроченным отпуском и создает алерты."""
        overdue_threshold_date = self.now - self.overdue_period
        logger.info(f"Checking for overdue coordinators. Threshold date: {overdue_threshold_date}")

        # Запрос с использованием подзапроса для получения последней даты ухода в отпуск
        latest_leave_subquery = (
            CoordinatorLogEvent.objects.filter(
                coordinator_id=OuterRef("pk"), type=self.leave_event_type
            )
            .order_by("-date_time")
            .values("date_time")[:1]
        )

        # Находим координаторов в отпуске с датой последнего события отпуска раньше порога
        overdue_coordinators = (
            Coordinator.objects.filter(project_status=CoordinatorProjectStatus.ON_LEAVE)
            .annotate(last_leave_date=Subquery(latest_leave_subquery))
            .filter(last_leave_date__lte=overdue_threshold_date)
        )

        logger.info(f"Found {overdue_coordinators.count()} overdue coordinators")

        if not overdue_coordinators.exists():
            logger.info("No overdue coordinators found")
            return

        # Получаем ID координаторов с просроченным отпуском
        overdue_ids = set(overdue_coordinators.values_list("pk", flat=True))
        logger.info(f"Overdue coordinator IDs: {overdue_ids}")

        # Находим координаторов, у которых уже есть активные алерты этого типа
        existing_alert_coord_ids = set(
            Alert.objects.filter(
                content_type=self.content_type,
                object_id__in=overdue_ids,
                alert_type=self.alert_type,
                is_resolved=False,
            ).values_list("object_id", flat=True)
        )
        logger.info(f"Existing alert coordinator IDs: {existing_alert_coord_ids}")

        # Создаем алерты для тех, у кого их еще нет
        alerts_to_create = []

        # Словарь для хранения дат ухода в отпуск (для оптимизации создания сообщений)
        leave_dates = {
            coord.pk: getattr(coord, "last_leave_date", None) for coord in overdue_coordinators
        }
        logger.info(f"Leave dates: {leave_dates}")

        for coord_id in overdue_ids:
            if coord_id not in existing_alert_coord_ids:
                leave_date = leave_dates.get(coord_id)
                details_msg = (
                    f"Status '{CoordinatorProjectStatus.ON_LEAVE.label}' set on "
                    f"{leave_date.strftime('%Y-%m-%d %H:%M')} is longer than "
                    f"{self.overdue_period.days} days."
                    if leave_date
                    else f"Status '{CoordinatorProjectStatus.ON_LEAVE.label}' is longer than "
                    f"{self.overdue_period.days} days."
                )
                alerts_to_create.append(
                    Alert(
                        content_type=self.content_type,
                        object_id=coord_id,
                        alert_type=self.alert_type,
                        details=details_msg,
                    )
                )
                logger.info(f"Prepared alert for coordinator {coord_id}: {details_msg}")

        self._bulk_create_alerts(alerts_to_create, processed_alerts)

    def resolve_alerts(self, processed_alerts: dict[str, int]) -> None:
        """Разрешает активные алерты о просроченном отпуске, если статус координатора изменился."""
        # Находим ID координаторов, связанных с активными алертами этого типа
        active_alerts = Alert.objects.filter(
            content_type=self.content_type, alert_type=self.alert_type, is_resolved=False
        )

        if not active_alerts.exists():
            return

        active_alert_coord_ids = list(active_alerts.values_list("object_id", flat=True))

        # Получаем текущие статусы координаторов
        coordinator_statuses = dict(
            Coordinator.objects.filter(pk__in=active_alert_coord_ids).values_list(
                "pk", "project_status"
            )
        )

        # Находим алерты для разрешения
        alerts_to_resolve_ids = []
        for alert in active_alerts:
            coord_id = alert.object_id
            # Если статус изменился с ON_LEAVE или координатор был удален
            if coordinator_statuses.get(coord_id) != CoordinatorProjectStatus.ON_LEAVE:
                alerts_to_resolve_ids.append(alert.pk)

        if alerts_to_resolve_ids:
            resolved_count = Alert.objects.filter(id__in=alerts_to_resolve_ids).update(
                is_resolved=True, resolved_at=self.now
            )
            logger.info(f"Resolved {resolved_count} {self.alert_type} alerts.")
            processed_alerts["resolved"] += resolved_count


# TODO: добавить другие обработчики для координаторов
# class CoordinatorLowActivityHandler(AlertHandler):
#     """Обработчик для координаторов с низкой активностью."""
#     ...
