from django.db import models

from api.models.age_range import AgeRange
from api.models.auxil.constants import DEFAULT_CHAR_FIELD_MAX_LEN
from api.models.language_and_level import Language
from api.models.student import Student


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

    def __str__(self) -> str:
        age_ranges = self.age_ranges.all()
        ages_text = (
            ", ".join(f"{age_range.age_from}-{age_range.age_to}" for age_range in age_ranges)
            if age_ranges
            else "all ages"
        )
        return f"{self.language} ({ages_text})"


class EnrollmentTestQuestion(models.Model):
    """Model for a question in a 'written' test given to the student at registration."""

    enrollment_test = models.ForeignKey(
        EnrollmentTest, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=DEFAULT_CHAR_FIELD_MAX_LEN)

    class Meta:
        constraints = [
            # accessing foreign key directly instead of making an additional query
            models.UniqueConstraint(
                fields=["enrollment_test_id", "text"], name="option_unique_per_test"
            ),
        ]

    def __str__(self) -> str:
        return self.text


class EnrollmentTestQuestionOption(models.Model):
    """Model for a possible answer to a question in a 'written' test."""

    question = models.ForeignKey(
        EnrollmentTestQuestion, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=50)
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            # accessing foreign key directly instead of making an additional query
            models.UniqueConstraint(
                fields=["question_id", "text"], name="option_unique_per_question"
            )
        ]

    def __str__(self) -> str:
        return f"{self.text} (*)" if self.is_correct else self.text


class EnrollmentTestResult(models.Model):
    """Model for a test result for a given student. Consists of answers to assessment questions."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollment_test_results"
    )
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)

    def __str__(self) -> str:
        return (
            f"Answers to enrollment test by {self.student} "
            f"({self.correct_answers_count} correct "
            f"out of {self.answers.count()} answers given)"
        )

    @property
    def correct_answers_count(self) -> int:
        return self.answers.filter(is_correct=True).count()
