from django.db import models
from django.utils.translation import gettext_lazy as _


class AgeRangeType(models.TextChoices):
    STUDENT = "student", _("for students to select their age")
    TEACHER = "teacher", _("for teacher to select desired ages of students")
    MATCHING = "matching", _("for matching algorithm")
