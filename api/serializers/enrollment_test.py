from collections.abc import Sequence

from rest_framework import serializers

from api.models import (
    EnrollmentTest,
    EnrollmentTestQuestion,
    EnrollmentTestQuestionOption,
    EnrollmentTestResult,
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
            "resulting_level",
        )

    # TODO Think about some validation, e.g. answers should be unique for each question
    #  and should be in options for this question


class EnrollmentTestResultLevelSerializer(serializers.ModelSerializer[EnrollmentTestResult]):
    """A serializer used to get level of language based on how many answers are correct."""

    @staticmethod
    def calculate_level(answer_ids: Sequence[int]) -> dict[str, str]:
        # returning dictionary to match regular JSON format
        return {"resulting_level": EnrollmentTestResult.calculate_level(answer_ids=answer_ids)}

    class Meta:
        model = EnrollmentTestResult
        fields = ("answers",)
