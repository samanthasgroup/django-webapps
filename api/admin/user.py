from collections.abc import Iterable
from typing import Any

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString

from api.models import Coordinator


class HasCoordinatorFilter(admin.SimpleListFilter):
    title = "Has Coordinator"
    parameter_name = "has_coordinator"

    def lookups(self, _request: HttpRequest, _model_admin: ModelAdmin[Any]) -> Iterable[tuple[Any, str]]:
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, _request: HttpRequest, queryset: QuerySet[User]) -> QuerySet[User]:
        value = self.value()
        if value == "yes":
            return queryset.filter(coordinator__isnull=False)
        if value == "no":
            return queryset.filter(coordinator__isnull=True)
        return queryset


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_coordinator",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "coordinator__personal_info__first_name",
        "coordinator__personal_info__last_name",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "groups",
        HasCoordinatorFilter,
    )

    @admin.display(description="Coordinator", ordering="coordinator__personal_info__id")
    def get_coordinator(self, obj: User) -> str | SafeString:
        try:
            coordinator = obj.coordinator
            url = reverse("admin:api_coordinator_change", args=[coordinator.pk])
            coordinator_show = f"{coordinator.pk} - {coordinator.personal_info.full_name}"
            return format_html('<a href="{}">{}</a>', url, coordinator_show)
        except Coordinator.DoesNotExist:
            return "-"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
