from typing import Any, cast

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from alerts.admin_inlines import AlertInline
from api.admin.auxil.widgets import PersonalInfoSelect2Widget
from api.models import Coordinator, Group, PersonalInfo, Teacher
from api.models.teacher import TeacherQuerySet


class HasGroupsFilter(SimpleListFilter):
    title = _("has groups")
    parameter_name = "has_groups"

    def lookups(
        self,
        request: HttpRequest,  # noqa: ARG002
        model_admin: admin.ModelAdmin[Any],  # noqa: ARG002
    ) -> list[tuple[str, str]]:
        return [
            ("yes", str(_("Yes"))),
            ("no", str(_("No"))),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Teacher]) -> TeacherQuerySet:  # noqa: ARG002
        teacher_queryset = cast(TeacherQuerySet, queryset)

        if self.value() == "yes":
            return teacher_queryset.filter_has_groups()
        if self.value() == "no":
            return teacher_queryset.filter_has_no_groups()
        return teacher_queryset


class CoordinatorFilter(admin.SimpleListFilter):
    title = _("координатор")
    parameter_name = "coordinator"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]  # noqa: ARG002
    ) -> list[tuple[str, str]]:
        qs = Coordinator.objects.select_related("personal_info").order_by(
            "personal_info__last_name", "personal_info__first_name"
        )
        return [(c.pk, str(f"{c.pk} - {c.personal_info.full_name}")) for c in qs]

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[PersonalInfo]  # noqa: ARG002
    ) -> QuerySet[PersonalInfo]:
        if self.value():
            return queryset.filter(groups__coordinators__pk=self.value())
        return queryset


class TeachersGroupInline(admin.TabularInline):  # type: ignore
    readonly_fields = ("group",)
    can_delete = False
    can_add = False
    extra = 0
    max_num = 0
    model = Group.teachers.through
    verbose_name_plural = _("Active groups")


class TeacherAdminForm(forms.ModelForm[Teacher]):
    class Meta:
        model = Teacher
        fields = "__all__"  # noqa: DJ007
        widgets = {
            "personal_info": PersonalInfoSelect2Widget,
        }

    class Media:
        css = {"all": ("css/select2-darkmode.css",)}
        js = ("admin/js/sticky-scroll-bar.js",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin[Teacher]):
    form = TeacherAdminForm

    class Media:
        css = {"all": ("css/admin-alerts-highlight.css",)}
        js = ("admin/js/sticky-scroll-bar.js", "admin/js/admin-alerts-highlight.js")

    list_display: tuple[str, ...] = (
        "get_pk",
        "get_full_name",
        "project_status",
        "roles_display",
        "coordinators_display",
        "get_personal_info_email",
        "get_personal_info_tg",
        "groups_links",
        "can_host_speaking_club",
        "teaching_languages_and_levels_display",
        "non_teaching_help_provided_display",
        "display_active_alerts_count",
    )

    list_filter = (
        "project_status",
        "roles",
        HasGroupsFilter,
        "groups",
        CoordinatorFilter,
        ("alerts__alert_type", admin.AllValuesFieldListFilter),
        ("alerts__is_resolved", admin.BooleanFieldListFilter),
    )

    search_fields: tuple[str, ...] = (
        "personal_info__pk",
        "personal_info__first_name__icontains",
        "personal_info__last_name__icontains",
        "personal_info__telegram_username__icontains",
        "roles__name__icontains",
    )

    inlines = [
        TeachersGroupInline,
        AlertInline,
    ]

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["title"] = "База учителей"
        return super().changelist_view(request, extra_context)

    def change_view(
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        extra_context = extra_context or {}
        if object_id:
            obj = self.get_object(request, object_id)
            if obj:
                extra_context["title"] = "Редактирование учителя"
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["title"] = "Добавить учителя"
        return super().add_view(request, form_url, extra_context)

    def get_queryset(self, request: HttpRequest) -> TeacherQuerySet:
        queryset_from_super = super().get_queryset(request)

        teacher_queryset = cast(TeacherQuerySet, queryset_from_super)

        return teacher_queryset.annotate(
            active_alerts_count=Count("alerts__pk", filter=Q(alerts__is_resolved=False), distinct=True)
        ).prefetch_related(
            "personal_info",
            "teaching_languages_and_levels",
            "availability_slots",
            "non_teaching_help_provided",
            "groups__coordinators__personal_info",
            "groups",
            "roles",
        )

    @admin.display(description=_("Roles"))
    def roles_display(self, obj: Teacher) -> str:
        return ", ".join([str(role) for role in obj.roles.all()])

    @admin.display(description=_("TID"))
    def get_pk(self, obj: Teacher) -> str:
        return obj.pk

    @admin.display(description=_("Full name"))
    def get_full_name(self, obj: Teacher) -> str:
        if hasattr(obj, "personal_info") and obj.personal_info:
            return f"{obj.personal_info.first_name} {obj.personal_info.last_name}"
        return str(_("N/A"))

    @admin.display(description=_("Has groups"))
    def groups_links(self, obj: Teacher) -> str:
        return obj.get_groups_links

    @admin.display(description=_("Teaching languages"))
    def teaching_languages_and_levels_display(self, obj: Teacher) -> str:
        return ", ".join([str(lang) for lang in obj.teaching_languages_and_levels.all()])

    @admin.display(description=_("Availability slots"))
    def availability_slots_display(self, obj: Teacher) -> str:
        slots = obj.availability_slots.select_related("time_slot").order_by(
            "day_of_week_index", "time_slot__from_utc_hour"
        )
        grouped: dict[str, list[str]] = {}
        for slot in slots:
            day = slot.get_day_of_week_index_display()
            start = slot.time_slot.from_utc_hour.strftime("%H:%M")
            end = slot.time_slot.to_utc_hour.strftime("%H:%M")
            grouped.setdefault(day, []).append(f"{start}–{end}")
        lines = [f"{day}: {', '.join(times)}" for day, times in grouped.items()]
        return mark_safe("<br>".join(lines))

    @admin.display(description=_("Non-teaching help provided"))
    def non_teaching_help_provided_display(self, obj: Teacher) -> str:
        return ", ".join([str(help_prov) for help_prov in obj.non_teaching_help_provided.all()])

    @admin.display(description=_("Coordinators"))
    def coordinators_display(self, obj: Teacher) -> str:
        unique_coordinators = {}
        for group in obj.groups.all():
            for coordinator in group.coordinators.all():
                if coordinator.pk not in unique_coordinators:
                    unique_coordinators[coordinator.pk] = coordinator

        if not unique_coordinators:
            return str(_("No coordinators"))

        links = []
        for coordinator in unique_coordinators.values():
            url = reverse("admin:api_coordinator_change", args=[coordinator.pk])
            coord_pi_pk = coordinator.personal_info.pk
            links.append(format_html('<a href="{}">{}</a>', url, coord_pi_pk))

        return format_html(", ".join(links))

    @admin.display(description=_("Active Alerts"), ordering="active_alerts_count")
    def display_active_alerts_count(self, obj: Teacher) -> int | str:
        count = getattr(obj, "active_alerts_count", None)
        if count is None:
            count = obj.alerts.filter(is_resolved=False).count()
        label = str(count) if count > 0 else "-"
        return format_html('<span class="active-alerts-count" data-count="{}">{}</span>', count, label)

    @admin.display(boolean=True, description=_("Can take more groups"))
    def can_take_more_groups_display(self, obj: Teacher) -> bool:
        return obj.can_take_more_groups

    @admin.display(description="Email", ordering="personal_info__email")
    def get_personal_info_email(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.email if coordinator.personal_info else ""

    @admin.display(description="Telegram", ordering="personal_info__telegram_username")
    def get_personal_info_tg(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.telegram_username if coordinator.personal_info else ""
