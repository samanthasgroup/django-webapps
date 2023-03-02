from django.db import models

from api.models.auxil import MultilingualModel


class CommunicationLanguageMode(MultilingualModel):
    """Model for 'language mode' (in class or maybe also communication with coordinators).

    These language modes are **mutually exclusive** and are intended to be used to match students
    and teachers into groups.
    """

    # planned possible values for name_internal: "ru" (Russian only), "ua" (Ukrainian only),
    # "ru_ua" (both Russian and Ukrainian), and "l2_only" (the teacher can only speak L2 language,
    # not to be confused with the teacher knowing Russian/Ukrainian but trying to speak L2 as much
    # as possible).
    # I don't think it should be imported in admin.py: the set of modes is very unlikely to change.


class TeachingLanguage(MultilingualModel):
    """Model for languages that students learn and teachers teach."""

    # TODO make it into internal model? Bot stores names of languages in its CSV


class LanguageLevel(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rank = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class TeachingLanguageAndLevel(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Teaching languages with levels"

    def __str__(self):
        return f"{self.language} - {self.level}"
