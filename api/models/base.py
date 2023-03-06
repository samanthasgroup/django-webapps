from django.db import models

from api.models.constants import DEFAULT_CHAR_FIELD_MAX_LEN


class ModelWithName(models.Model):
    name_internal = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            "Internal name to use in code. This will allow to change user-facing names easily "
            "without breaking the code. Internal name must not change after adding it."
        ),
        verbose_name="internal name",
    )

    class Meta:
        abstract = True


class ModelWithMultilingualName(ModelWithName):
    """Abstract model for end-user facing entities that need names to be stored in 3 languages."""

    name_en = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True, verbose_name="name in English"
    )
    name_ru = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True, verbose_name="name in Russian"
    )
    name_ua = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True, verbose_name="name in Ukrainian"
    )

    class Meta:
        abstract = True
        # it is possible that some user-facing names will be repeated; internal names are unique
        constraints = [
            models.UniqueConstraint(fields=["name_internal"], name="f%(class)s_name_internal")
        ]

    def __str__(self):
        return self.name_en


class InternalModelWithName(ModelWithName):
    """Abstract model for internal entities that have a name attribute but do not need to support
    internationalization.
    """

    name_for_user = models.CharField(max_length=100, verbose_name="Readable name for coordinator")

    class Meta:
        abstract = True
        # This has to be repeated: the constraint will not be inherited from parent class.
        constraints = [
            models.UniqueConstraint(fields=["name_internal"], name="f%(class)s_name_internal")
        ]

    def __str__(self):
        return self.name_for_user
