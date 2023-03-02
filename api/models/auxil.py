from django.db import models


class MultilingualModel(models.Model):
    """Abstract model for end-user facing entities that need names to be stored in 3 languages."""

    name_internal = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            "Internal name to use in code. This will allow to change user-facing names easily "
            "without breaking the code."
        ),
    )
    name_en = models.CharField(max_length=255, unique=True)
    name_ru = models.CharField(max_length=255, unique=True)
    name_ua = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True  # This model will not be used to create any database table

    def __str__(self):
        return self.name_en


class InternalModelWithName(models.Model):
    """Abstract model for internal entities that have a name attribute but do not need to support
    internationalization.
    """

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
