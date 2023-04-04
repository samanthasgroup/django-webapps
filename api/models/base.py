from django.db import models

from api.models.choices.communication_language_modes import CommunicationLanguageMode
from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class GroupOrPerson(models.Model):
    """Model holding attributes that are common for every person and group."""

    communication_language_mode = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CommunicationLanguageMode.choices,
        verbose_name="Language(s) the students and teachers can speak in class",
    )

    class Meta:
        abstract = True
