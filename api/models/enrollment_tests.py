from django.db import models

from api.models.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.languages_levels import TeachingLanguageAndLevel
from api.models.people import Student


class EnrollmentTest(models.Model):
    """Model for 'written' test given to the student at registration."""

    languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)

    def __str__(self):
        return ", ".join(self.languages_and_levels.all())


class EnrollmentTestQuestion(models.Model):
    enrollment_test = models.ForeignKey(EnrollmentTest, on_delete=models.CASCADE)
    text = models.CharField(max_length=DEFAULT_CHAR_FIELD_MAX_LEN, unique=True)

    def __str__(self):
        return self.text


class EnrollmentTestQuestionOption(models.Model):
    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            # accessing foreign key directly instead of making an additional query
            models.UniqueConstraint(
                fields=["question_id", "text"], name="option_unique_per_question"
            ),
            models.UniqueConstraint(
                fields=["question_id", "is_correct"], name="only_one_correct_option_per_question"
            ),
        ]

    def __str__(self):
        return f"{self.text} (*)" if self.is_correct else self.text


class EnrollmentTestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)

    def __str__(self):
        return f"Test results of {self.student}"
