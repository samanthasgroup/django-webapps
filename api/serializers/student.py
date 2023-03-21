from rest_framework import serializers

from api.models import Student
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)


class StudentWriteSerializer(serializers.ModelSerializer[Student]):
    class Meta:
        model = Student
        fields = "__all__"


class StudentReadSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeSerializer(read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = "__all__"
