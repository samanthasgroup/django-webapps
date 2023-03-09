from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class InternalModelWithName(models.Model):
    """Abstract model for internal entities that have a name attribute but do not need to support
    internationalization.
    """

    name_internal = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            "Internal name to use in code. This will allow to change user-facing names easily "
            "without breaking the code. Internal name must not change after adding it."
        ),
        verbose_name="internal name",
    )
    name_for_user = models.CharField(max_length=100, verbose_name="Readable name for coordinator")

    class Meta:
        abstract = True
        # This has to be repeated: the constraint will not be inherited from parent class.
        constraints = [
            models.UniqueConstraint(fields=["name_internal"], name="f%(class)s_name_internal")
        ]

    def __str__(self):
        return self.name_for_user


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
