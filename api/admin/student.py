from __future__ import annotations

from typing import Any

from django import forms
from django.contrib import admin
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from api import models
from api.admin.auxil.mixin import CoordinatorRestrictedAdminMixin
from api.models import Student
from api.models.coordinator import Coordinator


class StudentAdminForm(forms.ModelForm[models.Student]):
    class Meta:
        model = models.Student
        fields = (
            "personal_info",
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


@admin.register(Student)
class StudentAdmin(CoordinatorRestrictedAdminMixin, VersionAdmin):
    form = StudentAdminForm

    readonly_fields = (
        "enrollment_tests_summary",
        "enrollment_tests_result_answers",
        "smalltalk_test_result",
    )

    list_display = (
        "pk",
        "get_full_name",
        "project_status",
        "age_range",
        "is_member_of_speaking_club",
        "has_groups_display",
        "teaching_languages_and_levels_display",
        "coordinators_display",
    )

    list_filter = ("teaching_languages_and_levels",)

    search_fields = (
        "personal_info__pk",
        "personal_info__first_name",
        "personal_info__last_name",
        "personal_info__email",
    )

    # change_list_template = "admin/api/students/change_list.html"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Student]:

        return (
            super()
            .get_queryset(request)
            .prefetch_related("groups", "children", "groups__coordinators__personal_info")
        )

    @admin.display(description=_("Full Name"))
    def get_full_name(self, obj: Student) -> str:
        return f"{obj.personal_info.first_name} {obj.personal_info.last_name}"

    @admin.display(boolean=True, description=_("Has Groups"))
    def has_groups_display(self, obj: Student) -> bool:
        return obj.has_groups

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

    def enrollment_tests_summary(self, obj: Student) -> str:
        result = ""
        for idx, test_result in enumerate(obj.enrollment_test_results.all(), start=1):
            first_answer = test_result.answers.first()
            if not first_answer:
                continue
            question = first_answer.question
            if not question:
                continue
            result += (
                f"Test #{idx}, Total questions: {question.enrollment_test.questions.count()}, "
                f"Total answers: {test_result.answers.count()}, "
                f"Correct answers: {test_result.correct_answers_count}\n"
            )
        return result

    def enrollment_tests_result_answers(self, obj: Student) -> str:
        result = ""
        for idx, test_result in enumerate(obj.enrollment_test_results.all(), start=1):
            result += f"<b>Test #{idx}</b><br>"
            for answer in test_result.answers.all():
                result += f"{answer.question}, answer: <b>{answer}</b>, <br>"
            result += "<br><br>"
        return format_html(result)

    def filter_for_coordinator(self, qs: QuerySet[Any], coordinator: Coordinator) -> QuerySet[Any]:
        """Filter students: only from groups of coordinator or without groups."""
        qs = qs.annotate(group_count=Count("groups"))
        return qs.filter(Q(groups__coordinators=coordinator) | Q(group_count=0)).distinct()
