from django.db import models

from api.models.auxil.constants import LanguageLevelId

# Sometimes the languages and levels are needed separately, sometimes in combinations.
# This means that we cannot create a "choices" field for language or level.

"""Dictionary with names of levels ("A0", "A1" etc.) as values 
and their position in the enumeration as keys."""
LANGUAGE_LEVEL_ID_TO_INDEX = {level: index for index, level in enumerate(sorted(LanguageLevelId))}


class Language(models.Model):
    """Model for languages that students learn and teachers teach."""

    id = models.CharField(max_length=2, primary_key=True, verbose_name="locale")
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class LanguageLevel(models.Model):
    """Model for language levels. Will be pre-populated."""

    # This would be a good candidate for a `models.TextChoices` class, but EnrollmentTest
    # has a many-to-many relationship to LanguageLevel, which requires a table.

    # no need for auto-incrementing ID here as level is only 2 chars long
    id = models.CharField(max_length=2, primary_key=True)

    def __str__(self) -> str:
        return self.id

    @property
    def index(self) -> int:
        return LANGUAGE_LEVEL_ID_TO_INDEX[LanguageLevelId(self.id)]


class LanguageAndLevel(models.Model):
    """A model combining language and level.

    This model is needed for the cases when a student/teacher studies/teaches several languages,
    each at different level(s).
    """

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Languages with levels"

    def __str__(self) -> str:
        return f"{self.language} - {self.level}"
