from collections import OrderedDict
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
        fields = ("answers", "resulting_level")
        extra_kwargs = {"answers": {"write_only": True}}

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        number_of_answers = len(attrs["answers"])
        if number_of_answers not in ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS:
            raise serializers.ValidationError(
                f"Enrollment test with {number_of_answers} questions is not supported"
            )
        return attrs

    def get_resulting_level(self, obj: OrderedDict[str, Any]) -> str:
        """Calculates language level depending on amount of correct answers."""
        # level thresholds (= numbers of correct answers required to reach that level)
        # depend on total number of questions
        level_for_threshold = ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS[
            len(obj["answers"])
        ]

        number_of_correct_answers = len([answer for answer in obj["answers"] if answer.is_correct])

        level = LanguageLevelId.A0_BEGINNER
        for threshold in level_for_threshold:
            if number_of_correct_answers >= threshold:
                level = level_for_threshold[threshold]
            else:
                break

        return level
