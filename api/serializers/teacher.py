from rest_framework import serializers

from api.models import Teacher
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)


class TeacherWriteSerializer(serializers.ModelSerializer[Teacher]):
    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherReadSerializer(serializers.ModelSerializer[Teacher]):
    student_age_ranges = AgeRangeSerializer(many=True, read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"
