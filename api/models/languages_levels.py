from django.db import models

from api.models.auxil import MultilingualModel


class NativeLanguage(MultilingualModel):
    """Model for native languages of coordinators, students and teachers."""


class TeachingLanguage(MultilingualModel):
    """Model for languages that students learn and teachers teach."""

    # TODO make it into internal model? Bot stores names of languages in its CSV


class LanguageLevel(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rank = models.IntegerField(unique=True)


class TeachingLanguageAndLevel(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)
