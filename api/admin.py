from django import forms
from django.contrib import admin
from django.utils.html import format_html

from api import models
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

        if self.Meta.model.objects.filter(**params).exists():
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


admin.site.register(models.PersonalInfo, PersonalInfoAdmin)
admin.site.register(models.Student, StudentAdmin)

for model in (
    models.Coordinator,
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
