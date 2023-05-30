"""Minified group serializer put to external module to prevent circular dependency."""

from rest_framework import serializers

from api.models import Group
from api.serializers.language_and_level import MinifiedLanguageAndLevelSerializer
from api.serializers.teacher.minified import MinifiedTeacherSerializer


class MinifiedGroupSerializer(serializers.ModelSerializer[Group]):
    """Serializer for Group model with only id and name fields."""

    language_and_level = MinifiedLanguageAndLevelSerializer(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    teachers = MinifiedTeacherSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = (
            "language_and_level",
            "students_count",
            "teachers",
        )
