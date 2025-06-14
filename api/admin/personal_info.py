from typing import Any

from django import forms
from django.contrib import admin
from reversion.admin import VersionAdmin

from api import models
from api.models.personal_info import PersonalInfo
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

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean() or {}
        first = cleaned_data.get("first_name")
        last = cleaned_data.get("last_name")
        email = cleaned_data.get("email")

        if first and last and email:
            params = {
                "first_name": capitalize_each_word(first),
                "last_name": capitalize_each_word(last),
                "email": email.lower(),
            }
            if self.Meta.model.objects.filter(**params).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    "User with these first name, last name and email already exists, "
                    "although they may be written in different letter cases."
                )

        return cleaned_data


@admin.register(PersonalInfo)
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
