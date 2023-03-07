from django.db import models

from api.models.base import InternalModelWithName


class Language(InternalModelWithName):
    """Model for languages that students learn and teachers teach."""


class LanguageAndLevel(models.Model):
    class Level(models.TextChoices):
        A0 = "A0", "A0 (Starter)"
        A1 = "A1", "A1 (Beginner)"
        A2 = "A2", "A2 (Pre-Intermediate)"
        B1 = "B1", "B1 (Intermediate)"
        B2 = "B2", "B2 (Upper-Intermediate)"
        C1 = "C1", "C1 (Advanced)"
        # This school is definitely not for C2 students, so no C2

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    level = models.CharField(max_length=2, choices=Level.choices)

    class Meta:
        verbose_name_plural = "Languages with levels"

    def __str__(self):
        return f"{self.language} - {self.level}"
