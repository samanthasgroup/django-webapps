from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from reversion.admin import VersionAdmin

from api import models
from api.admin.auxil.mixin import CoordinatorRestrictedAdminMixin
from api.models import Coordinator

COMMON_SEARCH_FIELDS = [
    "personal_info__first_name__icontains",
    "personal_info__last_name__icontains",
    "personal_info__email__icontains",
    "personal_info__pk__iexact",
]


class StudentSelect2Widget(ModelSelect2MultipleWidget):
    model = models.Student
    search_fields = COMMON_SEARCH_FIELDS


class TeachersSelect2Widget(ModelSelect2MultipleWidget):
    model = models.Teacher
    search_fields = COMMON_SEARCH_FIELDS


class CoordinatorsSelect2Widget(ModelSelect2MultipleWidget):
    model = models.Coordinator
    search_fields = COMMON_SEARCH_FIELDS


class StaffOnlyFilter(admin.SimpleListFilter):
    title = _("is for staff only")
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


class CoordinatorFilter(admin.SimpleListFilter):
    title = _("Coordinator")
    parameter_name = "coordinator"

    def lookups(
        self, _request: HttpRequest, _model_admin: ModelAdmin[Any]
    ) -> list[tuple[int, str]]:
        coordinators = models.Coordinator.objects.all()
        return [(c.pk, str(c)) for c in coordinators]

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if self.value():
            return queryset.filter(coordinators__pk=self.value())
        return queryset


class ScheduleFilter(admin.SimpleListFilter):
    title = _("Schedule")
    parameter_name = "schedule"

    DAYS = [
        ("monday", _("Понедельник")),
        ("tuesday", _("Вторник")),
        ("wednesday", _("Среда")),
        ("thursday", _("Четверг")),
        ("friday", _("Пятница")),
        ("saturday", _("Суббота")),
        ("sunday", _("Воскресенье")),
    ]

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin[Any]) -> list[tuple[str, str]]:
        result = []
        qs = model_admin.get_queryset(request)
        for field_name, verbose_day in self.DAYS:
            day_qs = qs.filter(**{f"{field_name}__isnull": False}).order_by(field_name)
            times = day_qs.values_list(field_name, flat=True).distinct()
            for time in times:
                value = f"{field_name}:{time.isoformat()}"
                label = f"{verbose_day}, {time.strftime('%H:%M')}"
                result.append((value, label))
        return result

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        value = str(self.value())
        if value:
            try:
                field_name, time_str = value.split(":", 1)
            except ValueError:
                return queryset
            return queryset.filter(**{field_name: time_str})
        return queryset


class GroupAdminForm(forms.ModelForm[Any]):
    class Meta:
        model = models.Group
        fields = (
            "id",
            "legacy_gid",
            "language_and_level",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "lesson_duration_in_minutes",
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
        widgets = {
            "students": StudentSelect2Widget,
            "teachers": TeachersSelect2Widget,
            "coordinators": CoordinatorsSelect2Widget,
        }


class GroupAdmin(CoordinatorRestrictedAdminMixin, VersionAdmin):
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
        "get_project_status",
        "get_situational_status",
        "get_status_since",
        "staff_only",
    )
    ordering = ["id"]
    list_filter = (
        StaffOnlyFilter,
        "project_status",
        "situational_status",
        CoordinatorFilter,
        ScheduleFilter,
    )
    search_fields = (
        "coordinators__personal_info__first_name",
        "coordinators__personal_info__last_name",
        "teachers__personal_info__first_name",
        "teachers__personal_info__last_name",
        "legacy_gid",
    )

    fields = (
        "id",
        "legacy_gid",
        "language_and_level",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "lesson_duration_in_minutes",
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

    readonly_fields = (
        "id",
        "schedule_display",
    )

    class Media:
        css = {"all": ("css/select2-darkmode.css",)}
        js = ("admin/js/sticky-scroll-bar.js",)

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Any], search_term: str
    ) -> tuple[QuerySet[Any], bool]:
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term.isdigit():
            queryset |= self.model.objects.filter(
                coordinators__personal_info__id=search_term
            ) | self.model.objects.filter(teachers__personal_info__id=search_term)
        return queryset, use_distinct

    def filter_for_coordinator(self, qs: QuerySet[Any], coordinator: Coordinator) -> QuerySet[Any]:
        """Фильтрует группы только для текущего координатора."""
        return qs.filter(coordinators=coordinator)

    @admin.display(description=_("Start Date"))
    def get_start_date(self, group: models.Group) -> str:
        if group.start_date is not None:
            return format_html(
                "<span style='white-space: nowrap;'>{}</span>",
                group.start_date.strftime("%d-%m-%Y"),
            )
        return ""

    @admin.display(description=_("End Date"))
    def get_end_date(self, group: models.Group) -> str:
        if group.end_date is not None:
            return format_html(
                "<span style='white-space: nowrap;'>{}</span>", group.end_date.strftime("%d-%m-%Y")
            )
        return ""

    @admin.display(description=_("Status Since"))
    def get_status_since(self, group: models.Group) -> str:
        return format_html(
            "<span style='white-space: nowrap;'>{}</span>",
            group.status_since.strftime("%d-%m-%Y %H:%M"),
        )

    @admin.display(description=_("Coordinators"))
    def coordinators_list(self, group: models.Group) -> str:
        links = [
            format_html(
                '<a style="white-space: nowrap;" href="{}">{}</a>',
                reverse("admin:api_coordinator_change", args=(coordinator.pk,)),
                coordinator,
            )
            for coordinator in group.coordinators.all()
        ]
        return mark_safe(" ".join(links))

    @admin.display(description=_("Teachers"))
    def teachers_list(self, group: models.Group) -> str:
        links = [
            format_html(
                '<a style="white-space: nowrap;" href="{}">{}</a>',
                reverse("admin:api_teacher_change", args=(teacher.pk,)),
                teacher,
            )
            for teacher in group.teachers.all()
        ]
        return mark_safe(" ".join(links))

    @admin.display(description=mark_safe(_("Number Of<br>Students")))
    def students_count(self, group: models.Group) -> int:
        return group.students.count()

    @admin.display(description=_("Schedule"))
    def get_schedule(self, group: models.Group) -> str:
        days = (
            ("monday", _("Mo")),
            ("tuesday", _("Tu")),
            ("wednesday", _("We")),
            ("thursday", _("Th")),
            ("friday", _("Fr")),
            ("saturday", _("Sa")),
            ("sunday", _("Su")),
        )
        schedule = [
            f"{short_name} {getattr(group, day).strftime('%H:%M')}"
            for day, short_name in days
            if getattr(group, day)
        ]
        return mark_safe(",<br>".join(schedule))

    @admin.display(description=_("Schedule"))
    def schedule_display(self, group: models.Group) -> str:
        if not group.pk:
            return str(_("Schedule will be available after saving the group"))

        days = (
            ("monday", _("Понедельник")),
            ("tuesday", _("Вторник")),
            ("wednesday", _("Среда")),
            ("thursday", _("Четверг")),
            ("friday", _("Пятница")),
            ("saturday", _("Суббота")),
            ("sunday", _("Воскресенье")),
        )

        schedule_items = []
        for day, day_name in days:
            time_value = getattr(group, day)
            if time_value:
                schedule_items.append(f"{day_name}: {time_value.strftime('%H:%M')}")

        if schedule_items:
            return format_html("<br>".join(schedule_items))

        return str(_("No schedule set"))

    @admin.display(description=_("For Staff"))
    def staff_only(self, group: models.Group) -> str:
        if getattr(group, "is_for_staff_only"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    @admin.display(description=mark_safe(_("Project<br>status")))
    def get_project_status(self, group: models.Group) -> str:
        return group.get_project_status_display()

    @admin.display(description=mark_safe(_("Situational<br>Status")))
    def get_situational_status(self, group: models.Group) -> str:
        return group.get_situational_status_display()
