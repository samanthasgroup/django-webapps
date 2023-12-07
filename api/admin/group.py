from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from api import models


class StaffOnlyFilter(admin.SimpleListFilter):
    title = "is for staff only"
    parameter_name = "staff"

    def lookups(
        self, _request: HttpRequest, _model_admin: ModelAdmin[Any]
    ) -> tuple[tuple[bool, str], ...]:
        return (
            (True, "Yes"),
            (False, "No"),
        )

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if (value := self.value()) in {"True", "False"}:
            return queryset.filter(is_for_staff_only=(value == "True"))
        return queryset


class GroupAdminForm(forms.ModelForm):  # type: ignore
    class Meta:
        model = models.Group
        fields = (
            "id",
            "language_and_level",
            "coordinators",
            "teachers",
            "students",
            "start_date",
            "end_date",
            "project_status",
            "situational_status",
            "status_since",
            "is_for_staff_only",
        )


class GroupAdmin(VersionAdmin):
    form = GroupAdminForm
    list_display = (
        "id",
        "language_and_level",
        "coordinators_list",
        "teachers_list",
        "students_count",
        "get_start_date",
        "get_end_date",
        "get_schedule",
        "project_status",
        "situational_status",
        "get_status_since",
        "staff_only",
    )

    ordering = ["id"]

    list_filter = (
        StaffOnlyFilter,
        "project_status",
        "situational_status",
    )

    search_fields = (
        "coordinators__personal_info__first_name",
        "coordinators__personal_info__last_name",
        "teachers__personal_info__first_name",
        "teachers__personal_info__last_name",
    )

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Any], search_term: str
    ) -> tuple[QuerySet[Any], bool]:
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term.isdigit():
            queryset |= self.model.objects.filter(
                coordinators__personal_info__id=search_term
            ) | self.model.objects.filter(teachers__personal_info__id=search_term)
        return queryset, use_distinct

    @admin.display(description="Start Date")
    def get_start_date(self, group: models.Group) -> str:
        if group.start_date is not None:
            return format_html(
                "<span style='white-space: nowrap;'>{}</span>",
                group.start_date.strftime("%d-%m-%Y"),
            )
        return ""

    @admin.display(description="End Date")
    def get_end_date(self, group: models.Group) -> str:
        if group.end_date is not None:
            return format_html(
                "<span style='white-space: nowrap;'>{}</span>", group.end_date.strftime("%d-%m-%Y")
            )
        return ""

    @admin.display(description="Status Since")
    def get_status_since(self, group: models.Group) -> str:
        return format_html(
            "<span style='white-space: nowrap;'>{}</span>",
            group.status_since.strftime("%d-%m-%Y %H:%M"),
        )

    @admin.display(description="Coordinators")
    def coordinators_list(self, group: models.Group) -> str:
        links = [
            format_html(
                '<a style="white-space: nowrap;" href="{}">{}\n</a>',
                reverse("admin:api_coordinator_change", args=(coordinator.pk,)),
                coordinator.personal_info.pk_full_name,
            )
            for coordinator in group.coordinators.all()
        ]
        return mark_safe(" ".join(links))

    @admin.display(description="Teachers")
    def teachers_list(self, group: models.Group) -> str:
        links = [
            format_html(
                '<a style="white-space: nowrap;" href="{}">{}\n</a>',
                reverse("admin:api_teacher_change", args=(teacher.pk,)),
                teacher.personal_info.pk_full_name,
            )
            for teacher in group.teachers.all()
        ]
        return mark_safe(" ".join(links))

    @admin.display(description="Number of Students")
    def students_count(self, group: models.Group) -> int:
        return group.students.count()

    @admin.display(description="Schedule")
    def get_schedule(self, group: models.Group) -> str:
        days = (
            ("monday", "Mo"),
            ("tuesday", "Tu"),
            ("wednesday", "We"),
            ("thursday", "Th"),
            ("friday", "Fr"),
            ("saturday", "Sa"),
            ("sunday", "Su"),
        )
        schedule = [
            f"{short_name} {getattr(group, day).strftime('%H:%M')}"
            for day, short_name in days
            if getattr(group, day)
        ]
        return mark_safe(",<br>".join(schedule))

    @admin.display(description="For Staff")
    def staff_only(self, group: models.Group) -> str:
        if getattr(group, "is_for_staff_only"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""
