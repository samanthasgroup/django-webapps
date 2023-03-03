from django.db import models

from api.models.languages_levels import LanguageLevel, TeachingLanguage
from api.models.people import Student


class EnrollmentTest(models.Model):
    """Model for 'written' test given to the student at registration."""

    language = models.ForeignKey(TeachingLanguage, on_delete=models.PROTECT)
    levels = models.ManyToManyField(LanguageLevel)

    def __str__(self):
        return f"{self.language}, levels {', '.join(self.levels.all())}"


class EnrollmentTestQuestion(models.Model):
    enrollment_test = models.ForeignKey(EnrollmentTest, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.text


class EnrollmentTestQuestionOption(models.Model):
    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50, unique=True)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.text} (*)" if self.is_correct else self.text


class EnrollmentTestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)

    def __str__(self):
        return f"Test results of {self.student}"
