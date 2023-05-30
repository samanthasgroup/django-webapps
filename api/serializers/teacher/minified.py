"""Minified teacher serializer put to external module to prevent circular dependency."""
from rest_framework import serializers

from api.models import Teacher


class MinifiedTeacherSerializer(serializers.ModelSerializer[Teacher]):
    """Serializer for Teacher model with only id and full_name fields."""

    full_name = serializers.CharField(source="personal_info.full_name")
    id = serializers.IntegerField(source="personal_info_id")

    class Meta:
        model = Teacher
        fields = ("id", "full_name")
