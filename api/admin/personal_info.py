from django import forms
from django.contrib import admin

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

        if self.Meta.model.objects.filter(**params).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "User with these first name, last name and email already exists, "
                "although they may be written in different letter cases."
            )


class PersonalInfoAdmin(admin.ModelAdmin[models.PersonalInfo]):
    form = PersonalInfoAdminForm
