from django.db import models


class AgeRangeType(models.TextChoices):
    STUDENT = "student", "for students to select their age"
    TEACHER = "teacher", "for teacher to select desired ages of students"
    MATCHING = "matching", "for matching algorithm"
