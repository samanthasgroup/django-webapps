from django.db import models

from api.models.base import InternalModelWithName

# Sometimes the languages and levels are needed separately, sometimes in combinations.
# This means that we cannot create a "choices" field for language or level.


class Language(InternalModelWithName):
    """Model for languages that students learn and teachers teach."""


class LanguageLevel(models.Model):
    """Model for language levels. Will be pre-populated."""

    # This would be a good candidate for a `models.TextChoices` class, but EnrollmentTest
    # has a many-to-many relationship to LanguageLevel, which requires a table.

    # no need for auto-incrementing ID here as level is only 2 chars long
    id = models.CharField(max_length=2, primary_key=True)


class LanguageAndLevel(models.Model):
    """A model combining language and level. It is needed for the cases when a student/teacher
    studies/teaches several languages, each at different level(s).
    """

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Languages with levels"

    def __str__(self):
        return f"{self.language} - {self.level}"
