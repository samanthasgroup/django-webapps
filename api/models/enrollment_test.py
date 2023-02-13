from django.db import models

from api.models.languages_levels import LanguageLevel, TeachingLanguage
from api.models.people import Student


class EnrollmentTest(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.PROTECT)
    levels = models.ManyToManyField(LanguageLevel)


class EnrollmentTestQuestion(models.Model):
    enrollment_test = models.ForeignKey(EnrollmentTest, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, unique=True)


class EnrollmentTestQuestionOption(models.Model):
    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50, unique=True)
    is_correct = models.BooleanField()


class EnrollmentTestResult(models.Model):
    student_info = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)
