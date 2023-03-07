from django.db import models

from api.models.base import ModelWithMultilingualName


class CommunicationLanguageMode(ModelWithMultilingualName):
    """Model for 'language mode' (in class or maybe also communication with coordinators).

    These language modes are **mutually exclusive** and are intended to be used to match students
    and teachers into groups.
    """

    # planned possible values for name_internal: "ru" (Russian only), "ua" (Ukrainian only),
    # "ru_ua" (both Russian and Ukrainian), and "l2_only" (the teacher can only speak L2 language,
    # not to be confused with the teacher knowing Russian/Ukrainian but trying to speak L2 as much
    # as possible).
    # It probably should not be imported in admin.py: the set of modes is very unlikely to change.


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
