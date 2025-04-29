from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.age_range_type import AgeRangeType


class AgeRange(models.Model):
    """Model for age range.

    Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.

    Will be pre-populated.  If changing, care must be taken: the boundaries of bigger
    age ranges must match the boundaries of the smaller ones.
    """

    age_from = models.PositiveSmallIntegerField(verbose_name=_("Start of age range"))
    age_to = models.PositiveSmallIntegerField(verbose_name=_("End of age range (inclusive)"))
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=AgeRangeType.choices,
        verbose_name=_("Type of age range"),
        help_text=_("Who or what is this range designed for"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["age_from", "age_to", "type"], name="unique_age_and_type"
            )
        ]

    def __str__(self) -> str:
        return f"{self.age_from}-{self.age_to} [{self.type[0].upper()}]"
