from rest_framework import serializers

from api.models import Student
from api.serializers import (
    AgeRangeSerializer,
    DayAndTimeSlotSerializer,
    LanguageAndLevelSerializer,
)


class StudentWriteSerializer(serializers.ModelSerializer[Student]):
    class Meta:
        model = Student
        exclude = (
            "children",
            "status",
            "comment",
        )


class StudentReadSerializer(serializers.ModelSerializer[Student]):
    age_range = AgeRangeSerializer(read_only=True)
    teaching_languages_and_levels = LanguageAndLevelSerializer(many=True, read_only=True)
    availability_slots = DayAndTimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        # TODO: Do we need to exclude `children` here? Do we need them in API?
        #  If yes, then we need to decide how to show them. As nested students?
        exclude = ("children",)
