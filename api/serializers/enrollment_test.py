from typing import Any

from rest_framework import serializers

from api.models import (
    EnrollmentTest,
    EnrollmentTestQuestion,
    EnrollmentTestQuestionOption,
    EnrollmentTestResult,
)
from api.models.constants import (
    ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS,
    LanguageLevelId,
)


class EnrollmentTestQuestionOptionSerializer(
    serializers.ModelSerializer[EnrollmentTestQuestionOption]
):
    class Meta:
        model = EnrollmentTestQuestionOption
        fields = (
            "id",
            "text",
        )


class EnrollmentTestQuestionSerializer(serializers.ModelSerializer[EnrollmentTestQuestion]):
    options = EnrollmentTestQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = EnrollmentTestQuestion
        fields = (
            "id",
            "text",
            "options",
        )


class EnrollmentTestSerializer(serializers.ModelSerializer[EnrollmentTest]):
    questions = EnrollmentTestQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = EnrollmentTest
        fields = "__all__"


class EnrollmentTestResultCreateSerializer(serializers.ModelSerializer[EnrollmentTestResult]):
    class Meta:
        model = EnrollmentTestResult
        fields = (
            "student",
            "answers",
        )

    # TODO Think about some validation, e.g. answers should be unique for each question
    #  and should be in options for this question


class EnrollmentTestResultLevelSerializer(serializers.ModelSerializer[EnrollmentTestResult]):
    """A serializer used to get level of language based on how many answers are correct."""

    resulting_level = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentTestResult
        fields = ["answers", "resulting_level"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if len(attrs["answers"]) not in ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS:
            raise serializers.ValidationError(
                f"Enrollment test with {len(attrs['answers'])} questions is not supported"
            )
        return attrs

    def get_resulting_level(self, obj: Any) -> str:  # noqa
        """Calculates language level depending on amount of correct answers."""
        answer_ids = tuple(a.id for a in self.validated_data["answers"])
        # depending on number of questions in test, the thresholds are different
        total_answers = len(answer_ids)

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
