from rest_framework import serializers

from api.models import Student


class MinifiedStudentSerializer(serializers.ModelSerializer[Student]):
    """Serializer for Student model with only id and full_name fields."""

    full_name = serializers.CharField(source="personal_info.full_name")
    id = serializers.IntegerField(source="personal_info_id")

    class Meta:
        model = Student
        fields = ("id", "full_name")
