from rest_framework import serializers

from api.models import Student
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)
from api.serializers.age_range import AgeRangeStringSerializer
from api.serializers.day_and_time_slot import MinifiedDayAndTimeSlotSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.utc_timedelta import UTCTimedeltaField


class StudentWriteSerializer(serializers.ModelSerializer[Student]):
    class Meta:
        model = Student
        exclude = (
            "children",
            "status",
        )


class StudentReadSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeSerializer(read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        exclude = ("children",)


class PublicStudentSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeStringSerializer()
    teaching_languages_and_levels = MinifiedLanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = MinifiedDayAndTimeSlotSerializer(many=True, read_only=True)
    id = serializers.IntegerField(source="personal_info_id")
    first_name = serializers.CharField(source="personal_info.first_name")
    last_name = serializers.CharField(source="personal_info.last_name")
    utc_timedelta = UTCTimedeltaField(source="personal_info.utc_timedelta")
    communication_language_mode = serializers.CharField(
        source="personal_info.communication_language_mode"
    )

    class Meta:
        model = Student
        fields = (
            "id",
            "first_name",
            "last_name",
            "comment",
            "utc_timedelta",
            "availability_slots",
            "communication_language_mode",
            "age_range",
            "status",
            "is_member_of_speaking_club",
            "teaching_languages_and_levels",
        )
