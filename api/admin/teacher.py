from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from api.models import Teacher
from api.models.coordinator import Coordinator


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin[Teacher]):
    list_display: tuple[str, ...] = (
        "pk",
        "get_full_name",
        "project_status",
        "has_groups_display",
        "can_host_speaking_club",
        "teaching_languages_and_levels_display",
        # "availability_slots_display",
        "non_teaching_help_provided_display",
        "coordinators_display",
    )

    search_fields: tuple[str, ...] = (
        "personal_info__pk",
        "personal_info__first_name__icontains",
        "personal_info__last_name__icontains",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Teacher]:
        # return super().get_queryset(request)
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("groups__coordinators__personal_info")

    @admin.display(description=_("Full name"))
    def get_full_name(self, obj: Teacher) -> str:
        return f"{obj.personal_info.first_name} {obj.personal_info.last_name}"

    @admin.display(boolean=True, description=_("Can take more groups"))
    def can_take_more_groups_display(self, obj: Teacher) -> bool:
        return obj.can_take_more_groups

    @admin.display(boolean=True, description=_("Has groups"))
    def has_groups_display(self, obj: Teacher) -> bool:
        return obj.has_groups

    @admin.display(description=_("Teaching languages"))
    def teaching_languages_and_levels_display(self, obj: Teacher) -> str:
        return ", ".join([str(lang) for lang in obj.teaching_languages_and_levels.all()])

    @admin.display(description=_("Availability slots"))
    def availability_slots_display(self, obj: Teacher) -> str:
        return "\n ".join([str(slot) for slot in obj.availability_slots.all()])

    @admin.display(description=_("Non-teaching help provided"))
    def non_teaching_help_provided_display(self, obj: Teacher) -> str:
        return ", ".join([str(help_prov) for help_prov in obj.non_teaching_help_provided.all()])

    @admin.display(description=_("Coordinators"))
    def coordinators_display(self, obj: Teacher) -> str:
        coordinators = Coordinator.objects.filter(groups__in=obj.groups.all()).distinct()
        if not coordinators:
            return str(_("No coordinators"))

        links = []
        for coordinator in coordinators:
            url = reverse("admin:api_coordinator_change", args=[coordinator.pk])
            full_name = coordinator.personal_info.full_name
            links.append(format_html('<a href="{}">{}</a>', url, full_name))

        return format_html(", ".join(links))
