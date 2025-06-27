from django import forms
from django_select2.forms import ModelSelect2Widget

from api import models


class PersonalInfoSelect2Widget(ModelSelect2Widget):
    """Select2 widget for selecting personal info records."""

    model = models.PersonalInfo
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
        "pk__iexact",
    ]


class NativeTimeInput(forms.TimeInput):
    """HTML5 time input widget with minute precision."""

    input_type = "time"

    def __init__(self, attrs: dict[str, str] | None = None) -> None:
        attrs = {"step": "60", "lang": "ru", **(attrs or {})}
        super().__init__(format="%H:%M", attrs=attrs)
