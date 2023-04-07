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
        exclude = ("levels",)


class EnrollmentTestResultCreateSerializer(serializers.ModelSerializer[EnrollmentTestResult]):
    class Meta:
        model = EnrollmentTestResult
        fields = (
            "student",
            "answers",
            "is_passed",
            "right_answers_percentage",
        )

    # TODO Think about some validation, e.g. answers should be unique for each question
    #  and should be in options for this question
