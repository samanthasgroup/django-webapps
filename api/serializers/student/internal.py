from typing import Any

from rest_framework import serializers

from api.exceptions import ConflictError
from api.models import LanguageAndLevel, Student
from api.models.choices.status.project import StudentProjectStatus
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)


class StudentWriteSerializer(serializers.ModelSerializer[Student]):
    teaching_languages_and_levels = serializers.PrimaryKeyRelatedField(
        queryset=LanguageAndLevel.objects.all(), required=False, allow_empty=True, many=True
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        project_status = None
        levels = None
        if self.instance is not None:
            project_status = self.instance.project_status  # type: ignore
            levels = self.instance.teaching_languages_and_levels  # type: ignore
        if attrs.get("project_status"):
            project_status = attrs.get("project_status")
        if attrs.get("teaching_languages_and_levels"):
            levels = attrs.get("teaching_languages_and_levels")
        if (
            project_status
            and not levels
            and project_status != StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL.value
        ):
            raise ConflictError(
                """Poject status should be only needs_interview_to_determine_level 
                   if language and level is not specified"""
            )

        return attrs

    class Meta:
        model = Student
        exclude = ("children",)


class StudentReadSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeSerializer(read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        exclude = ("children",)
