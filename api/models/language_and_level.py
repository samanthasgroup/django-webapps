from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import LanguageLevelId

# Sometimes the languages and levels are needed separately, sometimes in combinations.
# This means that we cannot create a "choices" field for language or level.

LANGUAGE_LEVEL_ID_TO_INDEX = {level: index for index, level in enumerate(sorted(LanguageLevelId))}
"""Dictionary with names of levels ("A0", "A1" etc.) as values 
and their position in the enumeration as keys."""


class Language(models.Model):
    """Model for languages that students learn and teachers teach."""

    id = models.CharField(max_length=2, primary_key=True, verbose_name=_("locale"))
    name = models.CharField(max_length=50, verbose_name=_("name"))

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")

    def __str__(self) -> str:
        return self.name


class LanguageLevel(models.Model):
    """Model for language levels. Will be pre-populated."""

    # This would be a good candidate for a `models.TextChoices` class, but EnrollmentTest
    # has a many-to-many relationship to LanguageLevel, which requires a table.

    # no need for auto-incrementing ID here as level is only 2 chars long
    id = models.CharField(max_length=2, primary_key=True, verbose_name=_("level id"))

    class Meta:
        verbose_name = _("language level")
        verbose_name_plural = _("language levels")

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

    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name=_("language"))
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE, verbose_name=_("level"))

    class Meta:
        verbose_name = _("language with level")
        verbose_name_plural = _("languages with levels")

    def __str__(self) -> str:
        return f"{self.language} {self.level}"
