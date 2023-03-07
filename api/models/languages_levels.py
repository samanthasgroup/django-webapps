from django.db import models

from api.models.base import ModelWithMultilingualName


class TeachingLanguage(ModelWithMultilingualName):
    """Model for languages that students learn and teachers teach."""

    # TODO make it into internal model? Bot stores names of languages in its CSV


class TeachingLanguageAndLevel(models.Model):
    class Level(models.TextChoices):
        A0 = "A0", "A0 (Starter)"
        A1 = "A1", "A1 (Beginner)"
        A2 = "A2", "A2 (Pre-Intermediate)"
        B1 = "B1", "B1 (Intermediate)"
        B2 = "B2", "B2 (Upper-Intermediate)"
        C1 = "C1", "C1 (Advanced)"
        # This school is definitely not for C2 students, so no C2

    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.CharField(max_length=2, choices=Level.choices)

    class Meta:
        verbose_name_plural = "Teaching languages with levels"

    def __str__(self):
        return f"{self.language} - {self.level}"
