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


class TeachersFilter(admin.SimpleListFilter):
    title = "teacher name"
    parameter_name = "teacher"

    def lookups(
        self, _request: HttpRequest, _model_admin: ModelAdmin[models.Teacher]
    ) -> list[tuple[int, str]]:
        teachers = (
            models.Teacher.objects.select_related("personal_info")
            .values_list(
                "personal_info__id", "personal_info__first_name", "personal_info__last_name"
            )
            .distinct()
            .order_by("personal_info__first_name", "personal_info__last_name")
        )
        return [(teacher_id, f"{first} {last}") for teacher_id, first, last in teachers]

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if value := self.value():
            return queryset.filter(teachers__personal_info__id=value)
        return queryset


class CoordinatorsFilter(admin.SimpleListFilter):
    title = "coordinator name"
    parameter_name = "coordinator"

    def lookups(
        self, _request: HttpRequest, _model_admin: ModelAdmin[models.Coordinator]
    ) -> list[tuple[int, str]]:
        coordinators = (
            models.Coordinator.objects.select_related("personal_info")
            .values_list(
                "personal_info__id", "personal_info__first_name", "personal_info__last_name"
            )
            .distinct()
            .order_by("personal_info__first_name", "personal_info__last_name")
        )
        return [(coord_id, f"{first} {last}") for coord_id, first, last in coordinators]

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if value := self.value():
            return queryset.filter(coordinators__personal_info__id=value)
        return queryset


class StaffOnlyFilter(admin.SimpleListFilter):
    title = "Staff Only"
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
        "start_date",
        "end_date",
        "get_schedule",
        "project_status",
        "situational_status",
        "status_since",
        "staff_only",
    )

    list_filter = (
        StaffOnlyFilter,
        "project_status",
        "situational_status",
        TeachersFilter,
        CoordinatorsFilter,
    )

    search_fields = (
        "coordinators__personal_info__first_name",
        "coordinators__personal_info__last_name",
        "teachers__personal_info__first_name",
        "teachers__personal_info__last_name",
    )

    def coordinators_list(self, obj: models.Group) -> str:
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:api_coordinator_change", args=(coordinator.pk,)),
                coordinator.personal_info.full_name,
            )
            for coordinator in obj.coordinators.all()
        ]
        return mark_safe(", ".join(links))

    coordinators_list.short_description = "Coordinators"  # type: ignore

    def teachers_list(self, obj: models.Group) -> str:
        links = [
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:api_teacher_change", args=(teacher.pk,)),
                teacher.personal_info.full_name,
            )
            for teacher in obj.teachers.all()
        ]
        return mark_safe(", ".join(links))

    teachers_list.short_description = "Teachers"  # type: ignore

    def students_count(self, obj: models.Group) -> int:
        return obj.students.count()

    students_count.short_description = "Number of students"  # type: ignore

    def get_schedule(self, obj: models.Group) -> str:
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
            f"{short_name}: {getattr(obj, day).strftime('%H:%M')}"
            for day, short_name in days
            if getattr(obj, day)
        ]
        return mark_safe(",<br>".join(schedule))

    get_schedule.short_description = "Schedule"  # type: ignore
    get_schedule.allow_tags = True  # type: ignore

    def staff_only(self, obj: models.Group) -> str:
        if getattr(obj, "is_for_staff_only"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    staff_only.short_description = "For Staff"  # type: ignore
