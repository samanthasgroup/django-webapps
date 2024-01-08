from django import forms
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from api import models


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


class StudentAdmin(VersionAdmin):
    form = StudentAdminForm
    readonly_fields = (
        "enrollment_tests_summary",
        "enrollment_tests_result_answers",
        "smalltalk_test_result",
    )

    # TODO: searching is case-sensitive, better to make it case-insensitive somehow
    search_fields = (
        "personal_info__first_name",
        "personal_info__last_name",
        "personal_info__email",
    )

    def enrollment_tests_summary(self, obj: models.Student) -> str:
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

    def enrollment_tests_result_answers(self, obj: models.Student) -> str:
        result = ""
        for idx, test_result in enumerate(obj.enrollment_test_results.all(), start=1):
            result += f"<b>Test #{idx}</b><br>"
            for answer in test_result.answers.all():
                result += f"{answer.question}, answer: <b>{answer}</b>, <br>"
            result += "<br><br>"
        return format_html(result)
