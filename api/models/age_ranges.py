from django.db import models

from api.models.choices.age_range_type import AgeRangeType
from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class AgeRange(models.Model):
    """Model for age range.

    Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.

    Will be pre-populated.  If changing, care must be taken: the boundaries of bigger
    age ranges must match the boundaries of the smaller ones.
    """

    age_from = models.PositiveSmallIntegerField()
    age_to = models.PositiveSmallIntegerField(verbose_name="End of age range (inclusive)")
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=AgeRangeType.choices,
        help_text="who/what is this range designed for",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["age_from", "age_to", "type"], name="unique_age_and_type"
            )
        ]

    def __str__(self) -> str:
        return f"{self.age_from}-{self.age_to} [{self.type[0].upper()}]"
