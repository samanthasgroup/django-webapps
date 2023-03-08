from django.db import models

from api.models.base import InternalModelWithName

# Sometimes the languages and levels are needed separately, sometimes in combinations.
# This means that we cannot create a "choices" field for language or level.


class Language(InternalModelWithName):
    """Model for languages that students learn and teachers teach."""


class LanguageLevel(InternalModelWithName):
    """Model for language levels. Will be pre-populated."""


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
