from collections.abc import Callable

import reversion
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.db.models import QuerySet
from django.http import HttpRequest
from reversion.admin import VersionAdmin

from api import models
from api.models import Group
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


class CoordinatorAdmin(VersionAdmin):
    list_display = (
        "__str__",
        "active_groups_count",
    )
    readonly_fields = ("active_groups_count",)
    inlines = [
        CoordinatorActiveGroupsInline,
        CoordinatorFormerGroupsInline,
        CoordinatorLogEventsInline,
    ]
    action_form = GroupActionForm

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
