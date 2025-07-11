from typing import Any

from django import forms
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from reversion.admin import VersionAdmin

from api import models
from api.admin.auxil.mixin import CoordinatorRestrictedAdminMixin
from api.admin.group import (
    COMMON_SEARCH_FIELDS,
    CoordinatorsSelect2Widget,
    FormerCoordinatorsSelect2Widget,
    StudentSelect2Widget,
    TeachersSelect2Widget,
)


class LanguageSelect2Widget(ModelSelect2Widget):
    model = models.Language
    search_fields = ["name__icontains", "id__icontains"]


class TeachersUnder18Select2Widget(ModelSelect2MultipleWidget):
    model = models.TeacherUnder18
    search_fields = COMMON_SEARCH_FIELDS


class SpeakingClubAdminForm(forms.ModelForm[models.SpeakingClub]):
    class Meta:
        model = models.SpeakingClub
        fields = (
            "id",
            "language",
            "is_for_children",
            "coordinators",
            "coordinators_former",
            "teachers",
            "teachers_under_18",
            "teachers_former",
            "students",
            "students_former",
            "comment",
            "telegram_chat_url",
        )
        widgets = {
            "language": LanguageSelect2Widget,
            "coordinators": CoordinatorsSelect2Widget,
            "coordinators_former": FormerCoordinatorsSelect2Widget,
            "teachers": TeachersSelect2Widget,
            "teachers_under_18": TeachersUnder18Select2Widget,
            "teachers_former": TeachersSelect2Widget,
            "students": StudentSelect2Widget,
            "students_former": StudentSelect2Widget,
        }


class SpeakingClubAdmin(CoordinatorRestrictedAdminMixin, VersionAdmin):
    form = SpeakingClubAdminForm
    readonly_fields = ("id",)

    class Media:
        css = {"all": ("css/select2-darkmode.css",)}
        js = ("admin/js/sticky-scroll-bar.js",)

    def filter_for_coordinator(self, qs: Any, coordinator: models.Coordinator) -> Any:
        return qs.filter(coordinators=coordinator)
