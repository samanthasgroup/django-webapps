from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Alert(models.Model):
    """
    Generic Alert model to flag issues related to any model instance.
    Uses GenericForeignKey to link to the related object.
    """

    # TODO:добавить choices для возомжных типов вместо просто строки
    alert_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Alert Type"),
        help_text=_(
            "A unique identifier for the type of alert (e.g., 'overdue_on_leave', 'low_student_activity')."
        ),
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    resolved_at = models.DateTimeField(
        null=True, blank=True, db_index=True, verbose_name=_("Resolved At")
    )
    is_resolved = models.BooleanField(default=False, db_index=True, verbose_name=_("Is Resolved"))
    details = models.TextField(blank=True, verbose_name=_("Details"))

    # --- Generic Foreign Key Fields ---
    # Ссылка на модель (Coordinator, Student, Group, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Related Model Type"),
        limit_choices_to={
            "model__in": ["coordinator", "group", "student", "teacher"],
            "app_label": "api",
        },
    )
    # Primary Key связанного объекта
    object_id = models.PositiveIntegerField(verbose_name=_("Related Object ID"))
    # "Виртуальное" поле для удобного доступа к связанному объекту (Coordinator, Student...)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = _("Alert")
        verbose_name_plural = _("Alerts")
        ordering = ["-created_at"]
        indexes = [
            # Индекс для быстрого поиска всех алертов для конкретного объекта
            models.Index(fields=["content_type", "object_id"], name="alert_content_object_idx"),
            # Индекс для поиска активных алертов определенного типа
            models.Index(fields=["alert_type", "is_resolved"], name="alert_type_resolved_idx"),
        ]

    def __str__(self) -> str:
        status = "Resolved" if self.is_resolved else "Active"
        try:
            # Попытка получить имя модели и объекта для лучшего __str__
            model_class = self.content_type.model_class()
            model_name = model_class.__name__ if model_class is not None else "UnknownModel"
            obj_str = str(self.content_object) if self.content_object else f"ID: {self.object_id}"
            return f"Alert '{self.alert_type}' for {model_name} ({obj_str}) - {status}"
        except Exception:  # На случай если content_type или object_id некорректны
            return f"Alert '{self.alert_type}' (Type: {self.content_type_id}, ID: {self.object_id}) - {status}"

    def resolve(self) -> None:
        """Marks the alert as resolved."""
        if not self.is_resolved:
            self.is_resolved = True
            self.resolved_at = timezone.now()
            self.save(update_fields=["is_resolved", "resolved_at"])
