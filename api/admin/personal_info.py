from django import forms
from reversion.admin import VersionAdmin

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


class PersonalInfoAdmin(VersionAdmin):
    form = PersonalInfoAdminForm

    list_display = (
        "first_name",
        "last_name",
        "email",
        "telegram_username",
        "registration_telegram_bot_language",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
