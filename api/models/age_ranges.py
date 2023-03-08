from django.db import models


class AgeRange(models.Model):
    """Model for age range.  Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.
    """

    age_from = models.PositiveSmallIntegerField()
    age_to = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["age_from", "age_to"], name="age_from_to")]

    def __str__(self):
        return f"Age {self.age_from} to {self.age_to}"
