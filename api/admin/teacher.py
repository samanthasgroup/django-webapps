from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from api.models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin[Teacher]):
    list_display: tuple[str, ...] = (
        "pk",
        "get_full_name",
        "project_status",
        "situational_status",
        "has_prior_teaching_experience",
        "can_take_more_groups_display",
        "has_groups_display",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Teacher]:
        return super().get_queryset(request)

    @admin.display(description=_("Full name"))
    def get_full_name(self, obj: Teacher) -> str:
        return f"{obj.personal_info.first_name} {obj.personal_info.last_name}"

    @admin.display(boolean=True, description=_("Can take more groups"))
    def can_take_more_groups_display(self, obj: Teacher) -> bool:
        return obj.can_take_more_groups

    @admin.display(boolean=True, description=_("Has groups"))
    def has_groups_display(self, obj: Teacher) -> bool:
        return obj.has_groups
