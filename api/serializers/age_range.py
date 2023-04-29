from rest_framework import serializers

from api.models import AgeRange


class AgeRangeSerializer(serializers.ModelSerializer[AgeRange]):
    class Meta:
        model = AgeRange
        fields = "__all__"


class AgeRangeStringField(serializers.Field):  # type: ignore
    """Field represents AgeRange as a string without type."""

    def to_representation(self, value: AgeRange) -> str:
        return f"{value.age_from}-{value.age_to}"
