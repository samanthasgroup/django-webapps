from django.db import models

from api.models.age_ranges import AgeRange
from api.models.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.languages_levels import Language, LanguageLevel
from api.models.people import Student


class EnrollmentTest(models.Model):
    """Model for 'written' test given to the student at registration."""

    # null=True has no effect on ManyToManyField.
    age_ranges = models.ManyToManyField(
        AgeRange,
        blank=True,
        help_text="age ranges for which this test was designed. "
        "Leave blank for the test to be shown to all ages.",
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    levels = models.ManyToManyField(
        LanguageLevel,
        blank=True,
        help_text="level(s) of the language this test was designed for. "
        "Leave blank for the test to be shown for all levels.",
    )

    def __str__(self):
        ages, levels = self.age_ranges.all(), self.levels.all()
        ages_text = ", ".join(ages) if ages else "all ages"
        levels_text = ", ".join(levels) if levels else "all levels"
        return f"{self.language} ({levels_text}, {ages_text})"


class EnrollmentTestQuestion(models.Model):
    """Model for a question in a 'written' test given to the student at registration."""

    enrollment_test = models.ForeignKey(EnrollmentTest, on_delete=models.CASCADE)
    text = models.CharField(max_length=DEFAULT_CHAR_FIELD_MAX_LEN)

    class Meta:
        constraints = [
            # accessing foreign key directly instead of making an additional query
            models.UniqueConstraint(
                fields=["enrollment_test_id", "text"], name="option_unique_per_test"
            ),
        ]

    def __str__(self):
        return self.text


class EnrollmentTestQuestionOption(models.Model):
    """Model for a possible answer to a question in a 'written' test."""

    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            # accessing foreign key directly instead of making an additional query
            models.UniqueConstraint(
                fields=["question_id", "text"], name="option_unique_per_question"
            )
        ]

    def __str__(self):
        return f"{self.text} (*)" if self.is_correct else self.text


class EnrollmentTestResult(models.Model):
    """Model for a test result for a given student. Consists of answers to assessment questions."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)

    def __str__(self):
        return f"Test results of {self.student}"
