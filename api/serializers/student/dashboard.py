from typing import Any

from rest_framework import serializers

from api.exceptions import ConflictError, UnproccessableEntityError
from api.models import Coordinator, DayAndTimeSlot, Group, LanguageAndLevel, Student
from api.serializers import DashboardPersonalInfoSerializer
from api.serializers.age_range import AgeRangeStringField
from api.serializers.day_and_time_slot import MinifiedDayAndTimeSlotSerializer
from api.serializers.group.minified import MinifiedGroupSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.non_teaching_help import NonTeachingHelpSerializerField
from api.serializers.shared import PersonTransferSerializer
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
            "legacy_sid",
            "first_name",
            "last_name",
            "comment",
            "utc_timedelta",
            "availability_slots",
            "communication_language_mode",
            "age_range",
            "project_status",
            "situational_status",
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


class DashboardStudentTransferSerializer(PersonTransferSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        validated_attrs = super().validate(attrs)
        to_group = validated_attrs["to_group"]
        from_group = validated_attrs["from_group"]
        if self.instance is not None and to_group.students.filter(pk=self.instance.pk).exists():
            raise ConflictError(
                f"Student {self.instance.pk} is already in that group {to_group.pk}"
            )

        if (
            self.instance is not None
            and not from_group.students.filter(pk=self.instance.pk).exists()
        ):
            raise ConflictError(f"Student {self.instance.pk} must be in group {from_group.pk}")

        return validated_attrs


class DashboardStudentMissedClassSerializer(serializers.Serializer[Any]):
    group_id = serializers.IntegerField()
    notified = serializers.BooleanField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            group = Group.objects.get(pk=int(attrs["group_id"]))
        except Group.DoesNotExist:
            raise UnproccessableEntityError(f"Group {attrs['group_id']} not found")

        if self.instance is not None and not group.students.filter(pk=self.instance.pk).exists():
            raise ConflictError(f"Student {self.instance.pk} is not in group {group.pk}")

        attrs["group"] = group

        return attrs


class DashboardStudentAcceptedOfferedGroupSerializer(serializers.Serializer[Any]):
    group_id = serializers.IntegerField()
    coordinator_id = serializers.IntegerField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            group = Group.objects.get(pk=int(attrs["group_id"]))
        except Group.DoesNotExist:
            raise UnproccessableEntityError(f"Group {attrs['group_id']} not found")

        if self.instance is not None and group.students.filter(pk=self.instance.pk).exists():
            raise ConflictError(f"Student {self.instance.pk} is already in group {group.pk}")

        attrs["group"] = group

        try:
            coordinator = Coordinator.objects.get(pk=int(attrs["coordinator_id"]))
        except Coordinator.DoesNotExist:
            raise UnproccessableEntityError(f"Coordinator {attrs['coordinator_id']} not found")

        attrs["coordinator"] = coordinator

        return attrs


class DashboardStudentOfferJoinGroupSerializer(serializers.Serializer[Any]):
    group_id = serializers.IntegerField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            group = Group.objects.get(pk=int(attrs["group_id"]))
        except Group.DoesNotExist:
            raise UnproccessableEntityError(f"Group {attrs['group_id']} not found")

        if self.instance is not None and group.students.filter(pk=self.instance.pk).exists():
            raise ConflictError(f"Student {self.instance.pk} is already in group {group.pk}")

        attrs["group"] = group

        return attrs


class DashboardAvailableStudentsSerializer(serializers.Serializer[Any]):
    time_slot_ids = serializers.ListField(child=serializers.IntegerField(), min_length=2)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        for time_slot_id in attrs["time_slot_ids"]:
            try:
                DayAndTimeSlot.objects.get(pk=time_slot_id)
            except DayAndTimeSlot.DoesNotExist:
                raise UnproccessableEntityError(f"Time slot {time_slot_id} not found")
        return attrs


class DashboardCompletedOralInterviewSerializer(serializers.Serializer[Any]):
    language_and_level_id = serializers.IntegerField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            language_and_level = LanguageAndLevel.objects.get(pk=attrs["language_and_level_id"])
        except LanguageAndLevel.DoesNotExist:
            raise UnproccessableEntityError(
                f"Language and level {attrs['language_and_level_id']} not found"
            )
        attrs["language_and_level"] = language_and_level
        return attrs
