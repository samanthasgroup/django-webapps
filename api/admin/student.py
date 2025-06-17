from __future__ import annotations

from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget
from reversion.admin import VersionAdmin

from api import models
from api.admin.auxil.mixin import CoordinatorRestrictedAdminMixin
from api.models import Student
from api.models.age_range import AgeRange
from api.models.coordinator import Coordinator


class StudentAgeRangeFilter(SimpleListFilter):
    title = _("возраст")
    parameter_name = "age_range"

    def lookups(
        self, request: HttpRequest, model_admin: ModelAdmin[Student]
    ) -> list[tuple[str, str]]:
        qs = model_admin.get_queryset(request)
        used_ranges = qs.values_list("age_range", flat=True).distinct()

        ranges = AgeRange.objects.filter(id__in=used_ranges).order_by("age_from")

        return [(str(r.id), str(r)) for r in ranges]

    def queryset(self, _request: HttpRequest, queryset: QuerySet[Student]) -> QuerySet[Student]:
        if self.value():
            return queryset.filter(age_range=self.value())
        return queryset


class ChildrenSelect2Widget(ModelSelect2MultipleWidget):
    model = models.Student
    search_fields = [
        "children",
        "personal_info__pk",
        "personal_info__last_name",
        "personal_info__first_name",
    ]


class StudentAdminForm(forms.ModelForm[models.Student]):
    class Meta:
        model = models.Student
        fields = (
            "personal_info",
            "legacy_sid",
            "project_status",
            "situational_status",
            "status_since",
            "age_range",
            "teaching_languages_and_levels",
            "availability_slots",
            "is_member_of_speaking_club",
            "non_teaching_help_required",
            "can_read_in_english",
            "comment",
            "children",
        )
        widgets = {
            "children": ChildrenSelect2Widget,
        }

    class Media:
        css = {"all": ("css/select2-darkmode.css",)}


@admin.register(Student)
class StudentAdmin(CoordinatorRestrictedAdminMixin, VersionAdmin):
    form = StudentAdminForm

    readonly_fields = (
        "enrollment_tests_summary",
        "enrollment_tests_result_answers",
        "smalltalk_test_result",
    )

    list_display = (
        "get_pk",
        "get_full_name",
        "project_status",
        "age_range",
        "is_member_of_speaking_club",
        "groups_links",
        "teaching_languages_and_levels_display",
        "coordinators_display",
    )

    list_filter = (
        "teaching_languages_and_levels",
        "project_status",
        StudentAgeRangeFilter,
    )

    search_fields = (
        "personal_info__pk",
        "personal_info__first_name",
        "personal_info__last_name",
        "personal_info__email",
        "legacy_sid",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Student]:

        return (
            super()
            .get_queryset(request)
            .prefetch_related("groups", "children", "groups__coordinators__personal_info")
        )

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["title"] = "База студентов"
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
                extra_context["title"] = "Редактирование студента"
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["title"] = "Добавить студента"
        return super().add_view(request, form_url, extra_context)

    @admin.display(description=_("SID"))
    def get_pk(self, obj: Student) -> str:
        return f"{obj.pk}"

    @admin.display(description=_("Full Name"))
    def get_full_name(self, obj: Student) -> str:
        return f"{obj.personal_info.first_name} {obj.personal_info.last_name}"

    @admin.display(description=_("Has groups"))
    def groups_links(self, obj: Student) -> str:
        return obj.get_groups_links

    @admin.display(description=_("Teaching languages"))
    def teaching_languages_and_levels_display(self, obj: Student) -> str:
        return ", ".join([str(lang) for lang in obj.teaching_languages_and_levels.all()])

    @admin.display(description=_("Coordinators"))
    def coordinators_display(self, obj: Student) -> str | None:
        coordinators = Coordinator.objects.filter(groups__in=obj.groups.all()).distinct()
        if not coordinators:
            return str(_("No coordinators"))

        links = []
        for coordinator in coordinators:
            url = reverse("admin:api_coordinator_change", args=[coordinator.pk])
            full_name = coordinator.personal_info.full_name
            links.append(format_html('<a href="{}">{}</a>', url, full_name))

        return format_html(", ".join(links))

    @admin.display(description=_("Enrollment test summary"))
    def enrollment_tests_summary(self, obj: Student) -> str:
        result = ""
        for idx, test_result in enumerate(obj.enrollment_test_results.all(), start=1):
            first_answer = test_result.answers.first()
            if not first_answer:
                continue
            question = first_answer.question
            if not question:
                continue
            result += _(
                "Test #%(idx)d, Total questions: %(total)d, Total answers: %(answers)d, "
                "Correct answers: %(correct)d\n"
            ) % {
                "idx": idx,
                "total": question.enrollment_test.questions.count(),
                "answers": test_result.answers.count(),
                "correct": test_result.correct_answers_count,
            }
        return result

    @admin.display(description=_("Enrollment test summary"))
    def enrollment_tests_result_answers(self, obj: Student) -> str:
        result = ""
        for idx, test_result in enumerate(obj.enrollment_test_results.all(), start=1):
            result += format_html("<b>{}</b><br>", _("Test #%d") % idx)
            for answer in test_result.answers.all():
                result += format_html(
                    "{}: {}<br>",
                    answer.question,
                    _("answer: <b>%s</b>") % answer,
                )
            result += "<br><br>"
        return format_html(result)

    def filter_for_coordinator(self, qs: QuerySet[Any], coordinator: Coordinator) -> QuerySet[Any]:
        """Filter students: only from groups of coordinator or without groups."""
        qs = qs.annotate(group_count=Count("groups"))
        return qs.filter(Q(groups__coordinators=coordinator) | Q(group_count=0)).distinct()
