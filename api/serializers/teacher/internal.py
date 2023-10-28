from rest_framework import serializers

from api.models import LanguageAndLevel, Teacher
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
    NonTeachingHelpSerializer,
)


class TeacherWriteSerializer(serializers.ModelSerializer[Teacher]):
    teaching_languages_and_levels = serializers.PrimaryKeyRelatedField(
        queryset=LanguageAndLevel.objects.all(), required=False, allow_empty=True, many=True
    )

    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherReadSerializer(serializers.ModelSerializer[Teacher]):
    student_age_ranges = AgeRangeSerializer(many=True, read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(
        many=True, allow_empty=True, read_only=True
    )
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)
    non_teaching_help_provided = NonTeachingHelpSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"
