from collections.abc import Callable

from django import forms
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from api import models
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.processors.auxil.log_event_creator import CoordinatorAdminLogEventCreator
from api.utils import capitalize_each_word


class PersonalInfoAdminForm(forms.ModelForm[models.PersonalInfo]):
    class Meta:
        model = models.PersonalInfo
        # registration bot chat ID also excluded from the form: there is no way to set it manually
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "telegram_username",
            "utc_timedelta",
            "registration_telegram_bot_language",
            "chatwoot_conversation_id",
            "information_source",
        )

    def clean(self) -> None:
        params = {
            param: capitalize_each_word(self.cleaned_data[param])
            for param in ("first_name", "last_name")
        }
        params["email"] = self.cleaned_data["email"].lower()

        if self.Meta.model.objects.filter(**params).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "User with these first name, last name and email already exists, "
                "although they may be written in different letter cases."
            )


class PersonalInfoAdmin(admin.ModelAdmin[models.PersonalInfo]):
    form = PersonalInfoAdminForm


class StudentAdminForm(forms.ModelForm[models.Student]):
    class Meta:
        model = models.Student
        fields = "__all__"


class StudentAdmin(admin.ModelAdmin[models.Student]):
    form = StudentAdminForm
    readonly_fields = (
        "enrollment_tests_summary",
        "enrollment_tests_result_answers",
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


class CoordinatorAdmin(admin.ModelAdmin[models.Coordinator]):
    def _make_create_log_event_action(
        self, log_event_type: CoordinatorLogEventType
    ) -> Callable[..., None]:
        def action(
            _: admin.ModelAdmin[models.Coordinator],
            __: HttpRequest,
            queryset: QuerySet[models.Coordinator],
        ) -> None:
            for coordinator in queryset:
                CoordinatorAdminLogEventCreator.create(
                    coordinator=coordinator,
                    log_event_type=log_event_type,
                )

        action.short_description = f"Create log event: {log_event_type}"  # type: ignore

        return action

    def get_actions(
        self, request: HttpRequest
    ) -> dict[str, tuple[Callable[..., str], str, str] | None]:
        actions = super().get_actions(request)
        for log_event_type in list(CoordinatorLogEventType):
            actions[f"create_log_event_{log_event_type}"] = (  # type: ignore  # looks like stubs bug
                self._make_create_log_event_action(log_event_type),
                f"create_log_event_{log_event_type}",
                f"Create log event: {log_event_type}",
            )

        return actions


admin.site.register(models.PersonalInfo, PersonalInfoAdmin)
admin.site.register(models.Student, StudentAdmin)
admin.site.register(models.Coordinator, CoordinatorAdmin)

for model in (
    models.EnrollmentTest,
    models.EnrollmentTestQuestion,
    models.EnrollmentTestQuestionOption,
    models.EnrollmentTestResult,
    models.Group,
    models.SpeakingClub,
    models.Teacher,
    models.TeacherUnder18,
    models.Language,
    models.LanguageAndLevel,
    models.NonTeachingHelp,
):
    admin.site.register(model)
