from collections.abc import Sequence
from typing import Any

from django.db import models
from django.db.models import QuerySet

from api.models.age_ranges import AgeRange
from api.models.constants import (
    DEFAULT_CHAR_FIELD_MAX_LEN,
    ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS,
    LanguageLevelId,
)
from api.models.languages_levels import Language
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

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)

    def __str__(self) -> str:
        return f"Test results of {self.student}"

    @property
    def resulting_level(self) -> str:
        """Returns language level of the student based on amount of correct answers."""
        return self.calculate_level(self.answers.values_list("id", flat=True))

    @staticmethod
    def calculate_level(answer_ids: Sequence[int] | QuerySet[Any]) -> str:
        """Calculates language level depending on amount of correct answers."""
        # depending on number of questions in test, the thresholds are different
        total_answers = len(answer_ids)

        # All answers must be filled, so it is safe to check number of answers, not questions
        if total_answers not in ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS:
            raise NotImplementedError(
                f"Enrollment test with {total_answers} questions is not supported"
            )

        answers = EnrollmentTestQuestionOption.objects.filter(id__in=answer_ids)
        number_of_correct_answers = answers.filter(is_correct=True).count()
        level = LanguageLevelId.A0_BEGINNER
        for threshold in ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS[total_answers]:
            if number_of_correct_answers >= threshold:
                level = ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS[total_answers][
                    threshold
                ]
            else:
                break

        return level
