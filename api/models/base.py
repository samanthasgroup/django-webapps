from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class GroupOrPerson(models.Model):
    """Model holding attributes that are common for every person and group."""

    class CommunicationLanguageMode(models.TextChoices):
        RU_ONLY = "ru", "Russian only"
        UA_ONLY = "ua", "Ukrainian only"
        RU_OR_UA = "ru_ua", "Russian or Ukrainian"
        L2_ONLY = "l2_only", "Only language being taught"

    communication_language_mode = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CommunicationLanguageMode.choices,
        verbose_name="Language(s) the students and teachers can speak in class",
    )

    class Meta:
        abstract = True
