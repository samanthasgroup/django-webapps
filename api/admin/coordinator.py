from collections.abc import Callable

import reversion
from django import forms
from django.contrib import admin, messages
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


class GroupActionForm(ActionForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)


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
        "situational_status",
        "get_status_since",
        "active_groups_count",
        "get_communication_language_mode",
        "mentor",
        "get_comment",
    )

    ordering = ["personal_info_id"]

    list_filter = (
        "is_validated",
        "is_admin",
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
    )
    readonly_fields = ("active_groups_count",)
    inlines = [
        CoordinatorActiveGroupsInline,
        CoordinatorFormerGroupsInline,
        CoordinatorLogEventsInline,
    ]
    action_form = GroupActionForm

    @admin.display(description="ID")
    def get_personal_info_id(self, coordinator: Coordinator) -> int:
        return coordinator.personal_info.id

    @admin.display(description="Full name")
    def get_personal_info_full_name(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.full_name

    @admin.display(description="Valid")
    def get_is_validated(self, coordinator: Coordinator) -> str:
        if getattr(coordinator, "is_validated"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    @admin.display(description="Admin")
    def get_is_admin(self, coordinator: Coordinator) -> str:
        if getattr(coordinator, "is_admin"):
            return format_html('<img src="{}" alt="icon"/>', "/static/admin/img/icon-yes.svg")
        return ""

    @admin.display(description="Project status")
    def get_project_status(self, coordinator: Coordinator) -> str:
        return coordinator.project_status

    @admin.display(description="Status last changed")
    def get_status_since(self, coordinator: Coordinator) -> str:
        return coordinator.status_since.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(description="Skills")
    def get_additional_skills_comment(self, coordinator: Coordinator) -> str:
        return coordinator.additional_skills_comment

    @admin.display(description=format_html("Communication<br>language(s)"))
    def get_communication_language_mode(self, coordinator: Coordinator) -> str:
        return coordinator.personal_info.communication_language_mode

    @admin.display(description="Comment")
    def get_comment(self, coordinator: Coordinator) -> str:
        comment = coordinator.comment
        return format_html(
            '<div style="width: 300px; word-wrap: break-word; white-space: pre-line;">{}</div>',
            comment,
        )

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
                        group=Group.objects.get(pk=group_from_request)
                        if group_from_request
                        else None,
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
