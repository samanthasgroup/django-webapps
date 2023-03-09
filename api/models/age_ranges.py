from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


class AgeRange(models.Model):
    """Model for age range.  Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.
    """

    class Type(models.TextChoices):
        STUDENT = "student", "for students to select their age"
        TEACHER = "teacher", "for teacher to select desired ages of students"
        MATCHING = "matching", "for matching algorithm"

    age_from = models.PositiveSmallIntegerField()
    age_to = models.PositiveSmallIntegerField()
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=Type.choices,
        help_text="who/what is this range designed for",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["age_from", "age_to", "type"], name="unique_age_and_type"
            )
        ]

    def __str__(self):
        return f"Age {self.age_from} to {self.age_to}"
