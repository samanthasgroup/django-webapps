from rest_framework import serializers

from api.models import Group
from api.serializers import MinifiedStudentSerializer
from api.serializers.coordinator import MinifiedCoordinatorSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.teacher.minified import MinifiedTeacherSerializer


class CommonPublicGroupSerializer(serializers.ModelSerializer[Group]):
    coordinators = MinifiedCoordinatorSerializer(many=True, read_only=True)
    teachers = MinifiedTeacherSerializer(many=True, read_only=True)
    language_and_level = MinifiedLanguageAndLevelSerializer(read_only=True)

    class Meta:
        model = Group
        fields: tuple[str, ...] = (
            "id",
            "communication_language_mode",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "language_and_level",
            "lesson_duration_in_minutes",
            "status",
            "start_date",
            "end_date",
            "telegram_chat_url",
            "coordinators",
            "teachers",
            "is_for_staff_only",
        )


class PublicGroupSerializer(CommonPublicGroupSerializer):
    """Representation of a Group that is used in 'All groups' Tooljet view."""

    students_count = serializers.IntegerField(read_only=True)

    class Meta(CommonPublicGroupSerializer.Meta):
        fields = CommonPublicGroupSerializer.Meta.fields + (
            "students_count",  # This field will be added in ViewSet by annotating a QuerySet.
        )


class PublicGroupWithStudentsSerializer(CommonPublicGroupSerializer):
    students = MinifiedStudentSerializer(many=True, read_only=True)

    class Meta(CommonPublicGroupSerializer.Meta):
        fields = CommonPublicGroupSerializer.Meta.fields + ("students",)
