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
