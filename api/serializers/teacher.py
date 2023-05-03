from rest_framework import serializers

from api.models import Teacher
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
    NonTeachingHelpSerializer,
)


class TeacherWriteSerializer(serializers.ModelSerializer[Teacher]):
    class Meta:
        model = Teacher
        exclude = ("status",)


class TeacherReadSerializer(serializers.ModelSerializer[Teacher]):
    student_age_ranges = AgeRangeSerializer(many=True, read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)
    non_teaching_help_provided = NonTeachingHelpSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"


class MinifiedTeacherSerializer(serializers.ModelSerializer[Teacher]):
    """Serializer for Teacher model with only id and full_name fields."""

    full_name = serializers.CharField(source="personal_info.full_name")
    id = serializers.IntegerField(source="personal_info_id")

    class Meta:
        model = Teacher
        fields = ("id", "full_name")
