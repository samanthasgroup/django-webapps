from typing import Any

from rest_framework import serializers

from api.exceptions import ConflictError
from api.models import Teacher
from api.models.auxil.constants import (
    TEACHER_PEER_SUPPORT_FIELD_NAME_PREFIX,
    TEACHER_PEER_SUPPORT_OPTIONS,
)
from api.serializers import DashboardPersonalInfoSerializer
from api.serializers.age_range import AgeRangeStringField
from api.serializers.day_and_time_slot import MinifiedDayAndTimeSlotSerializer
from api.serializers.group.minified import MinifiedGroupSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.non_teaching_help import NonTeachingHelpSerializerField
from api.serializers.shared import PersonTransferSerializer
from api.serializers.utc_timedelta import UTCTimedeltaField


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


class CommonDashboardTeacherSerializer(serializers.ModelSerializer[Teacher]):
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
            "project_status",
            "situational_status",
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


class DashboardTeacherSerializer(CommonDashboardTeacherSerializer):
    """Representation of a Teacher that is used in 'All teachers' Tooljet view."""

    class Meta(CommonDashboardTeacherSerializer.Meta):
        pass


class DashboardTeacherWithPersonalInfoSerializer(CommonDashboardTeacherSerializer):
    """Representation of a Teacher that is used in 'Teacher by coordinator' Tooljet view."""

    personal_info = DashboardPersonalInfoSerializer()
    groups = MinifiedGroupSerializer(many=True, read_only=True)

    # TODO LogEvent ?

    class Meta(CommonDashboardTeacherSerializer.Meta):
        fields = CommonDashboardTeacherSerializer.Meta.fields + (
            "personal_info",
            "groups",
        )


class DashboardTeacherTransferSerializer(PersonTransferSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        validated_attrs = super().validate(attrs)
        to_group = validated_attrs["to_group"]
        from_group = validated_attrs["from_group"]
        if self.instance is not None and to_group.teachers.filter(pk=self.instance.pk).exists():
            raise ConflictError(
                f"Teacher {self.instance.pk} is already in that group {to_group.pk}"
            )

        if (
            self.instance is not None
            and not from_group.teachers.filter(pk=self.instance.pk).exists()
        ):
            raise ConflictError(f"Teacher {self.instance.pk} must be in group {from_group.pk}")

        return validated_attrs
