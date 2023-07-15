from rest_framework import serializers

from api.models import Student
from api.serializers import DashboardPersonalInfoSerializer
from api.serializers.age_range import AgeRangeStringField
from api.serializers.day_and_time_slot import MinifiedDayAndTimeSlotSerializer
from api.serializers.group.minified import MinifiedGroupSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.non_teaching_help import NonTeachingHelpSerializerField
from api.serializers.utc_timedelta import UTCTimedeltaField


class CommonDashboardStudentSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeStringField()
    teaching_languages_and_levels = MinifiedLanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = MinifiedDayAndTimeSlotSerializer(many=True, read_only=True)
    id = serializers.IntegerField(source="personal_info_id")
    first_name = serializers.CharField(source="personal_info.first_name")
    last_name = serializers.CharField(source="personal_info.last_name")
    utc_timedelta = UTCTimedeltaField(source="personal_info.utc_timedelta")
    communication_language_mode = serializers.CharField(
        source="personal_info.communication_language_mode"
    )
    non_teaching_help_required = NonTeachingHelpSerializerField()

    class Meta:
        model = Student
        fields: tuple[str, ...] = (
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
            "non_teaching_help_required",
        )


class DashboardStudentSerializer(CommonDashboardStudentSerializer):
    """Representation of a Student that is used in 'All students' Tooljet view."""

    class Meta(CommonDashboardStudentSerializer.Meta):
        pass


class DashboardStudentWithPersonalInfoSerializer(CommonDashboardStudentSerializer):
    """
    Representation of a Student with personal info that is used
    in 'Students by coordinator' Tooljet view.
    """

    personal_info = DashboardPersonalInfoSerializer(read_only=True)
    groups = MinifiedGroupSerializer(many=True, read_only=True)

    # TODO LogEvent?

    class Meta(CommonDashboardStudentSerializer.Meta):
        fields = CommonDashboardStudentSerializer.Meta.fields + (
            "personal_info",
            "groups",
        )