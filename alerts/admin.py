from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

from alerts.config import AlertConfig

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin[Alert]):
    list_display = (
        "pk",
        # "alert_type",
        "alert_type_badge",
        "content_object_link",
        "related_model_type",
        "created_at",
        "is_resolved",
        "resolved_at",
    )
    list_filter = ("alert_type", "is_resolved", "content_type", "created_at", "resolved_at")
    search_fields = (
        "alert_type",
        "object_id",
        "details",
    )
    readonly_fields = (
        "created_at",
        "resolved_at",
        "content_type",
        "object_id",
        "content_object_link",
    )
    # оптимизация запросов
    list_select_related = ("content_type",)
    date_hierarchy = "created_at"
    actions = ["mark_resolved"]

    fieldsets = (
        (None, {"fields": ("alert_type", "content_object_link", "details")}),
        ("Status", {"fields": ("is_resolved", "created_at", "resolved_at")}),
        # Скрываем поля GFK, показываем через content_object_link
        (
            "Related Object",
            {
                "fields": ("content_type", "object_id"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Related Object"))
    def content_object_link(self, obj: Alert) -> str:
        """Создает ссылку на админку связанного объекта, если возможно."""
        content_object = obj.content_object
        if content_object:
            try:
                opts = content_object._meta
                url = reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[content_object.pk])
                return format_html('<a href="{}">{}</a>', url, str(content_object))
            except Exception:
                return str(content_object)
        return "-"

    content_object_link.admin_order_field = "object_id"  # type: ignore[attr-defined]

    @admin.display(description=_("Model Type"))
    def related_model_type(self, obj: Alert) -> str:
        return obj.content_type.name.capitalize()

    related_model_type.admin_order_field = "content_type"  # type: ignore[attr-defined]

    @admin.action(description=_("Mark selected alerts as resolved"))
    def mark_resolved(self, request: HttpRequest, queryset: Any) -> None:
        updated_count = 0
        for alert in queryset.filter(is_resolved=False):
            alert.resolve()
            updated_count += 1
        self.message_user(request, _(f"{updated_count} alerts marked as resolved."))

    @admin.display(description=_("Type"))
    def alert_type_badge(self, obj: Alert) -> SafeString:
        style = AlertConfig.STYLES.get(obj.alert_type, "")
        label = obj.get_alert_type_display() if hasattr(obj, "get_alert_type_display") else obj.alert_type
        return format_html('<span style="padding:2px 6px; border-radius:4px; {}">{}</span>', style, label)
