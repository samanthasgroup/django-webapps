from collections.abc import Callable
from typing import Any

import reversion
from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.helpers import ActionForm
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from api import models
from api.models import Coordinator, Group
from api.models.choices.log_event_type import (
    COORDINATOR_LOG_EVENTS_REQUIRE_GROUP,
    CoordinatorLogEventType,
)
from api.processors.auxil.log_event_creator import CoordinatorAdminLogEventCreator


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
    )

    ordering = ["personal_info_id"]

    list_filter = (
        "is_validated",
        AdminStatusFilter,
        "project_status",
        "situational_status",
        "personal_info__communication_language_mode",
        "mentor",
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
    ]
    action_form = GroupActionForm

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

    def get_queryset(self, _: HttpRequest) -> QuerySet[models.Coordinator]:
        return models.Coordinator.objects.annotate_with_group_count().prefetch_related("groups")

    def active_groups_count(self, obj: models.Coordinator) -> int:
        return obj.groups.count()

    active_groups_count.admin_order_field = "group_count"  # type: ignore[attr-defined]

    def _make_create_log_event_action(
        self, log_event_type: CoordinatorLogEventType
    ) -> Callable[..., None]:
        def action(
            _: admin.ModelAdmin[models.Coordinator],
            request: HttpRequest,
            queryset: QuerySet[models.Coordinator],
        ) -> None:
            group_from_request = request.POST["group"]

            if log_event_type in COORDINATOR_LOG_EVENTS_REQUIRE_GROUP:
                if not group_from_request:
                    self.message_user(
                        request, "You should choose group for this action.", messages.ERROR
                    )
                    return
            elif group_from_request:
                self.message_user(
                    request,
                    "You should not choose group for this action.",
                    messages.ERROR,
                )
                return

            for coordinator in queryset:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(f"Created log event {log_event_type}")
                    CoordinatorAdminLogEventCreator.create(
                        coordinator=coordinator,
                        log_event_type=log_event_type,
                        group=(
                            Group.objects.get(pk=group_from_request)
                            if group_from_request
                            else None
                        ),
                    )

        return action

    def get_actions(
        self, request: HttpRequest
    ) -> dict[str, tuple[Callable[..., str], str, str] | None]:
        actions = super().get_actions(request)
        for log_event_type in list(CoordinatorLogEventType):
            actions[f"create_log_event_{log_event_type}"] = (
                self._make_create_log_event_action(log_event_type),
                f"create_log_event_{log_event_type}",
                # TODO: maybe some more human-readable description?
                f"Create log event: {log_event_type}",
            )

        return actions
