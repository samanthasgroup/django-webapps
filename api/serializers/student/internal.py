from rest_framework import serializers

from api.models import LanguageAndLevel, Student
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)


class StudentWriteSerializer(serializers.ModelSerializer[Student]):
    teaching_languages_and_levels = serializers.PrimaryKeyRelatedField(
        queryset=LanguageAndLevel.objects.all(), required=False, allow_empty=True, many=True
    )

    class Meta:
        model = Student
        exclude = ("children",)


class StudentReadSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeSerializer(read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        exclude = ("children",)
