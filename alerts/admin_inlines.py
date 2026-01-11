from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from alerts.config import AlertConfig
from alerts.models import Alert

DETAILS_PREVIEW_LENGTH = 80


class AlertInline(GenericTabularInline):
    """Inline admin for Alerts on a related object page."""

    model = Alert
    fields = (
        "alert_type_badge",
        "created_at",
        "is_resolved",
        "resolved_at",
        "details_link",
    )
    readonly_fields = ("alert_type_badge", "created_at", "resolved_at", "details_link")
    extra = 0
    ordering = (
        "-is_resolved",
        "-created_at",
    )  # active first, then newest
    ct_field = "content_type"
    ct_fk_field = "object_id"

    @admin.display(description=_("Type"), ordering="alert_type")
    def alert_type_badge(self, obj: Alert) -> str:
        style = AlertConfig.STYLES.get(obj.alert_type, "")
        label = obj.get_alert_type_display() if hasattr(obj, "get_alert_type_display") else obj.alert_type
        return format_html('<span style="padding:2px 6px; border-radius:4px; {}">{}</span>', style, label)

    @admin.display(description=_("Details"))
    def details_link(self, obj: Alert) -> str:
        if not obj.pk:
            return "-"
        link = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk])
        details = obj.details or ""
        preview = f"{details[:DETAILS_PREVIEW_LENGTH]}..." if len(details) > DETAILS_PREVIEW_LENGTH else details
        label = preview or str(_("View/Edit"))
        title = details or str(_("No details"))
        return format_html('<a href="{}" title="{}">{}</a>', link, title, label)
