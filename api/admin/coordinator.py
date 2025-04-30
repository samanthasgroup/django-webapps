import json
from typing import Any

import reversion
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.helpers import ActionForm
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from alerts.models import Alert
from api import models
from api.models import Coordinator, Group
from api.models.choices.log_event_type import (
    COORDINATOR_LOG_EVENTS_REQUIRE_GROUP,
    CoordinatorLogEventType,
)
from api.processors.auxil.log_event_creator import CoordinatorAdminLogEventCreator

DETAILS_PREVIEW_LENGTH: int = 30


class AlertInline(GenericTabularInline):
    """Inline admin for Alerts on a related object page."""

    model = Alert  # Указываем модель Alert
    fields = (
        "alert_type",
        "created_at",
        "is_resolved",
        "resolved_at",
        "details_link",
    )
    readonly_fields = ("alert_type", "created_at", "resolved_at", "details_link")
    extra = 0
    ordering = (
        "-is_resolved",
        "-created_at",
    )  # Сначала активные, потом новые
    ct_field = "content_type"  # Имя поля ContentType в Alert
    ct_fk_field = "object_id"  # Имя поля ID объекта в Alert

    # Опционально: ссылка на страницу деталей алерта

    @admin.display(description="Details")
    def details_link(self, obj: Alert) -> str:
        if not obj.pk:
            return "-"
        link: str = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk]
        )
        details_preview: str = (
            (obj.details[:DETAILS_PREVIEW_LENGTH] + "...")
            if len(obj.details) > DETAILS_PREVIEW_LENGTH
            else obj.details
        )
        return format_html('<a href="{}">{}</a>', link, details_preview or "View/Edit")

    # Показываем только активные, если нужно
    # def get_queryset(self, request):
    #    qs = super().get_queryset(request)
    #    return qs.filter(is_resolved=False)


class AdminStatusFilter(SimpleListFilter):
    title = "admin status"
    parameter_name = "is_admin"

    def lookups(
        self, _request: HttpRequest, _model_admin: ModelAdmin[Any]
    ) -> tuple[tuple[bool, str], ...]:
        return (
            (True, "Yes"),
            (False, "No"),
        )

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Coordinator]:
        if self.value() == "True":
            return queryset.filter(is_admin=True)
        if self.value() == "False":
            return queryset.filter(is_admin=False)
        return queryset


class BaseCoordinatorGroupInline(
    admin.TabularInline[
        models.Group.coordinators.through | models.Group.coordinators_former.through,  # type: ignore[name-defined]  # It can't see the "through" attribute.  # noqa: E501
        models.Coordinator,
    ]
):
    readonly_fields = ("group",)
    can_delete = False
    can_add = False
    extra = 0
    max_num = 0


class NameGroupChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj: Any) -> str:
        coordinators = ", ".join([str(c) for c in obj.coordinators.all()]).rstrip().strip()
        return f"Group {obj.pk}, {obj.language_and_level} (coords: {coordinators})"


class GroupActionForm(ActionForm):
    group = NameGroupChoiceField(
        queryset=Group.objects.all(),
        required=False,
    )


class CoordinatorActiveGroupsInline(BaseCoordinatorGroupInline):
    model = models.Group.coordinators.through
    verbose_name_plural = "Active groups"


class CoordinatorFormerGroupsInline(BaseCoordinatorGroupInline):
    model = models.Group.coordinators_former.through
    verbose_name_plural = "Former groups"


class CoordinatorLogEventsInline(
    admin.TabularInline[models.CoordinatorLogEvent, models.Coordinator]
):
    model = models.CoordinatorLogEvent
    can_delete = False
    readonly_fields = (
        "comment",
        "group",
        "type",
        "date_time",
    )
    extra = 0
    max_num = 0
    show_change_link = True


class CoordinatorForm(forms.ModelForm):  # type: ignore
    class Meta:
        model = models.Coordinator
        fields = (
            "is_validated",
            "is_admin",
            "personal_info",
            "additional_skills_comment",
            "role_comment",
            "project_status",
            "situational_status",
            "status_since",
            "mentor",
        )


class CoordinatorAdmin(VersionAdmin):
    form = CoordinatorForm
    list_display = (
        "get_personal_info_id",
        "get_personal_info_full_name",
        "get_is_validated",
        "get_is_admin",
        "get_additional_skills_comment",
        "get_project_status",
        "get_situational_status",
        "get_status_since",
        "active_groups_count",
        "get_communication_language_mode",
        "mentor",
        "get_comment",
        "get_role_comment",
        "display_active_alerts_count",
    )

    ordering = ["personal_info_id"]

    list_filter = (
        "is_validated",
        AdminStatusFilter,
        "project_status",
        "situational_status",
        "personal_info__communication_language_mode",
        "mentor",
        ("alerts__is_resolved", admin.BooleanFieldListFilter),
        ("alerts__alert_type", admin.AllValuesFieldListFilter),
    )

    search_fields = (
        "personal_info__id",
        "personal_info__first_name",
        "personal_info__last_name",
        "mentor__personal_info__id",
        "mentor__personal_info__first_name",
        "mentor__personal_info__last_name",
        "additional_skills_comment",
        "comment",
        "role_comment",
    )
    readonly_fields = ("active_groups_count",)
    inlines = [
        CoordinatorActiveGroupsInline,
        CoordinatorFormerGroupsInline,
        CoordinatorLogEventsInline,
        AlertInline,
    ]
    # action_form = GroupActionForm

    list_display_links = (
        "get_personal_info_id",
        "get_personal_info_full_name",
    )

    class Media:
        js = ("admin/js/sticky-scroll-bar.js",)

    @admin.display(description="ID", ordering="personal_info__id")
    def get_personal_info_id(self, coordinator: Coordinator) -> int:
        return coordinator.personal_info.id

    @admin.display(description="Full name", ordering="personal_info__first_name")
    def get_personal_info_full_name(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.full_name

    @admin.display(description="Valid", ordering="is_validated")
    def get_is_validated(self, coordinator: Coordinator) -> str:
        if getattr(coordinator, "is_validated"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    @admin.display(description="Admin", ordering="is_admin")
    def get_is_admin(self, coordinator: Coordinator) -> str:
        if getattr(coordinator, "is_admin"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    @admin.display(description=format_html("Project<br>status"), ordering="project_status")
    def get_project_status(self, coordinator: Coordinator) -> str:
        return coordinator.project_status.replace("_", " ")

    @admin.display(description=format_html("Situational<br>Status"), ordering="situational_status")
    def get_situational_status(self, coordinator: Coordinator) -> str:
        return coordinator.situational_status.replace("_", " ")

    @admin.display(description=format_html("Status<br>last changed"), ordering="status_since")
    def get_status_since(self, coordinator: Coordinator) -> str:
        date_str = coordinator.status_since.strftime("%Y-%m-%d")
        time_str = coordinator.status_since.strftime("%H:%M")
        return format_html("{} <br> {}", date_str, time_str)

    @admin.display(description="Skills", ordering="additional_skills_comment")
    def get_additional_skills_comment(self, coordinator: Coordinator) -> str:
        return coordinator.additional_skills_comment

    @admin.display(
        description=format_html("Communication<br>language(s)"),
        ordering="personal_info__communication_language_mode",
    )
    def get_communication_language_mode(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.communication_language_mode

    @admin.display(description="Comment")
    def get_comment(self, coordinator: Coordinator) -> str:
        comment = coordinator.comment
        return format_html(
            '<div style="max-width: 150px; word-wrap: break-word; '
            "overflow-wrap: break-word; white-space: "
            'pre-line;">{}</div>',
            comment,
        )

    @admin.display(description="Role", ordering="role_comment")
    def get_role_comment(self, coordinator: Coordinator) -> str:
        return coordinator.role_comment

    @admin.display(description=_("Active Alerts"), ordering="alerts__created_at")
    def display_active_alerts_count(self, obj: Coordinator) -> int | str:
        """Displays the count of active alerts."""
        count: int = obj.alerts.filter(is_resolved=False).count()
        return count if count > 0 else "-"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Coordinator]:
        # Оптимизация 1: аннотация с количеством групп
        # Оптимизация 2: предзагрузка групп
        # Оптимизация 3: предзагрузка алертов (если нужно)
        return (
            super()
            .get_queryset(request)
            .annotate(group_count=Count("groups"))
            .prefetch_related("groups")
            # .prefetch_related('alerts')
        )

    def active_groups_count(self, obj: models.Coordinator) -> int:
        return obj.groups.count()

    active_groups_count.admin_order_field = "group_count"  # type: ignore[attr-defined]

    def get_form(
        self, request: HttpRequest, obj: Coordinator | None = None, **kwargs: Any
    ) -> forms.ModelForm[Coordinator]:
        return super().get_form(request, obj, **kwargs)

    def change_view(  # noqa: PLR0911
        self,
        request: HttpRequest,
        object_id: str,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> Any:
        # Получаем контекст от родительского метода или создаем пустой словарь
        extra_context = extra_context or {}

        # Добавляем данные для наших выпадающих списков в контекст шаблона
        # Преобразуем Enum в словарь для удобства в шаблоне
        extra_context["log_event_type_choices"] = {
            event_type.value: event_type.label for event_type in CoordinatorLogEventType
        }
        extra_context["all_groups"] = (
            Group.objects.select_related("language_and_level")
            .prefetch_related("coordinators")
            .all()
        )

        # Передаем список типов, требующих группу, в формате JSON для JavaScript
        types_req_group_list = [t.value for t in COORDINATOR_LOG_EVENTS_REQUIRE_GROUP]
        extra_context["log_event_types_require_group_json"] = json.dumps(types_req_group_list)

        # --- Обработка НАШЕЙ кастомной отправки ---
        if request.method == "POST" and "_create_log_event" in request.POST:
            # Получаем координатора, к которому относится страница
            coordinator = self.get_object(request, object_id)
            if coordinator is None:
                # Обработка случая, если объект не найден (маловероятно, но возможно)
                self.message_user(request, "Coordinator not found.", messages.ERROR)
                return HttpResponseRedirect(request.path)  # Перезагружаем страницу

            # Извлекаем данные из POST
            log_event_type_str = request.POST.get("_log_event_type")
            group_id_str = request.POST.get("_log_event_group")
            group = None
            log_event_type = None

            # Валидация типа события
            if not log_event_type_str:
                self.message_user(request, "Event Type is required.", messages.ERROR)
                # Остаемся на той же странице, чтобы пользователь исправил
                return super().change_view(
                    request, object_id, form_url, extra_context=extra_context
                )

            try:
                # Пытаемся найти Enum по значению
                log_event_type = CoordinatorLogEventType(log_event_type_str)
            except ValueError:
                self.message_user(
                    request, f"Invalid Event Type: {log_event_type_str}.", messages.ERROR
                )
                return super().change_view(
                    request, object_id, form_url, extra_context=extra_context
                )

            # Валидация группы (как было в action)
            requires_group = log_event_type in COORDINATOR_LOG_EVENTS_REQUIRE_GROUP
            group_provided = bool(group_id_str)

            if requires_group and not group_provided:
                self.message_user(
                    request, "You must choose a group for this event type.", messages.ERROR
                )
                return super().change_view(
                    request, object_id, form_url, extra_context=extra_context
                )
            if not requires_group and group_provided:
                self.message_user(
                    request, "You should not choose a group for this event type.", messages.ERROR
                )
                return super().change_view(
                    request, object_id, form_url, extra_context=extra_context
                )
            if requires_group and group_provided:
                try:
                    assert group_id_str is not None
                    group = Group.objects.get(pk=int(group_id_str))
                except (ValueError, Group.DoesNotExist):
                    self.message_user(request, "Invalid Group selected.", messages.ERROR)
                    return super().change_view(
                        request, object_id, form_url, extra_context=extra_context
                    )

            # --- Если все проверки пройдены ---
            try:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(
                        f"Created log event {log_event_type} via admin change form"
                    )
                    CoordinatorAdminLogEventCreator.create(
                        coordinator=coordinator,
                        log_event_type=log_event_type,
                        group=group,
                    )

                event_name = (
                    log_event_type.label
                    if hasattr(log_event_type, "label")
                    else log_event_type.value
                )
                success_msg = f"Log event '{event_name}' created successfully."

                self.message_user(request, success_msg, messages.SUCCESS)

            except Exception as e:
                # Ловим возможные ошибки при создании лога
                self.message_user(request, f"Error creating log event: {e}", messages.ERROR)

            return HttpResponseRedirect(request.path)

        # --- Если это не наша отправка, вызываем стандартное поведение ---
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
