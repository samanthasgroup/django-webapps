from rest_framework import serializers

from api.models import enrollment_test


class EnrollmentTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = enrollment_test.EnrollmentTest
        fields = ["id"]


class EnrollmentTestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = enrollment_test.EnrollmentTestQuestion
        fields = ["id", "text"]


class EnrollmentTestQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = enrollment_test.EnrollmentTestQuestionOption
        fields = ["id", "text", "is_correct"]
