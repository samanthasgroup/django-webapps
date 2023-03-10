from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class AgeRangeType(models.TextChoices):
    STUDENT = "student", "for students to select their age"
    TEACHER = "teacher", "for teacher to select desired ages of students"
    MATCHING = "matching", "for matching algorithm"


class AgeRange(models.Model):
    """Model for age range.  Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.

    Will be pre-populated.  If changing, care must be taken: the boundaries of bigger
    age ranges must match the boundaries of the smaller ones.
    """

    # TODO split in 3 tables? Otherwise a teacher's age range can be chosen in Student.
    #  Maybe it's not a big deal, though
    age_from = models.PositiveSmallIntegerField()
    age_to = models.PositiveSmallIntegerField(verbose_name="End of age range (NOT inclusive!)")
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

    def __str__(self):
        return f"{self.age_from}-{self.age_to} [{self.type[0].upper()}]"
