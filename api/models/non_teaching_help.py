from django.db import models

from api.models.auxil.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.choices.non_teaching_help_type import NonTeachingHelpType


class NonTeachingHelp(models.Model):
    """Model for ways of helping students other than teaching them foreign languages.

    Both Student and Teacher can have connections to this model, meaning that a teacher can
    provide this kind of help, while a student requires this kind of help.
    """

    id = models.CharField(
        max_length=20, primary_key=True, choices=NonTeachingHelpType.choices
    )  # for easier connection with bot
    name = models.CharField(max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True)

    def __str__(self) -> str:
        return self.name
