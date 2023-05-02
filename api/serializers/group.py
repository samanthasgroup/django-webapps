from rest_framework import serializers

from api.models import Group
from api.serializers.coordinator import MinifiedCoordinatorSerializer
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.teacher import MinifiedTeacherSerializer


class PublicGroupSerializer(serializers.ModelSerializer[Group]):
    """Representation of a Group that is used in 'All groups' Tooljet view."""

    coordinators = MinifiedCoordinatorSerializer(many=True, read_only=True)
    teachers = MinifiedTeacherSerializer(many=True, read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    language_and_level = MinifiedLanguageAndLevelSerializer(read_only=True)

    class Meta:
        model = Group
        fields = (
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
            "students_count",  # This field will be added in ViewSet by annotating a QuerySet.
            "is_for_staff_only",
        )
