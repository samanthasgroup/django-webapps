from rest_framework import serializers

from api.models import Teacher
from api.models.auxil.constants import (
    TEACHER_PEER_SUPPORT_FIELD_NAME_PREFIX,
    TEACHER_PEER_SUPPORT_OPTIONS,
)
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
    NonTeachingHelpSerializer,
    PublicPersonalInfoSerializer,
)
from api.serializers.age_range import AgeRangeStringField
from api.serializers.day_and_time_slot import MinifiedDayAndTimeSlotSerializer
from api.serializers.group.minified import MinifiedGroupSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.non_teaching_help import NonTeachingHelpSerializerField
from api.serializers.utc_timedelta import UTCTimedeltaField


class TeacherWriteSerializer(serializers.ModelSerializer[Teacher]):
    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherReadSerializer(serializers.ModelSerializer[Teacher]):
    student_age_ranges = AgeRangeSerializer(many=True, read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)
    non_teaching_help_provided = NonTeachingHelpSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"


class PeerSupportField(serializers.SerializerMethodField):
    """
    Field to show fields with prefix from `TEACHER_PEER_SUPPORT_FIELD_NAME_PREFIX`
    as nested object of Teacher.
    """

    def to_representation(self, instance: Teacher) -> dict[str, bool]:
        return {
            field: getattr(instance, f"{TEACHER_PEER_SUPPORT_FIELD_NAME_PREFIX}{field}")
            for field in TEACHER_PEER_SUPPORT_OPTIONS
        }


class CommonPublicTeacherSerializer(serializers.ModelSerializer[Teacher]):
    id = serializers.IntegerField(source="personal_info_id")
    first_name = serializers.CharField(source="personal_info.first_name")
    last_name = serializers.CharField(source="personal_info.last_name")
    utc_timedelta = UTCTimedeltaField(source="personal_info.utc_timedelta")
    communication_language_mode = serializers.CharField(
        source="personal_info.communication_language_mode"
    )
    availability_slots = MinifiedDayAndTimeSlotSerializer(many=True, read_only=True)
    student_age_ranges = serializers.ListSerializer(child=AgeRangeStringField())  # type: ignore
    teaching_languages_and_levels = MinifiedLanguageAndLevelSerializer(many=True, read_only=True)
    non_teaching_help_provided = NonTeachingHelpSerializerField()
    peer_support = PeerSupportField()
    date_and_time_added = serializers.DateTimeField(source="personal_info.date_and_time_added")

    class Meta:
        model = Teacher
        fields: tuple[str, ...] = (
            "id",
            "first_name",
            "last_name",
            "status",
            "communication_language_mode",
            "utc_timedelta",
            "availability_slots",
            "student_age_ranges",
            "teaching_languages_and_levels",
            "simultaneous_groups",
            "weekly_frequency_per_group",
            "can_host_speaking_club",
            "non_teaching_help_provided_comment",
            "non_teaching_help_provided",
            "peer_support",
            "date_and_time_added",
        )
        read_only_fields = fields


class PublicTeacherSerializer(CommonPublicTeacherSerializer):
    """Representation of a Teacher that is used in 'All teachers' Tooljet view."""

    class Meta(CommonPublicTeacherSerializer.Meta):
        pass


class PublicTeacherWithPersonalInfoSerializer(CommonPublicTeacherSerializer):
    """Representation of a Teacher that is used in 'Teacher by coordinator' Tooljet view."""

    personal_info = PublicPersonalInfoSerializer()
    groups = MinifiedGroupSerializer(many=True, read_only=True)

    # TODO LogEvent ?

    class Meta(CommonPublicTeacherSerializer.Meta):
        fields = CommonPublicTeacherSerializer.Meta.fields + (
            "personal_info",
            "groups",
        )
