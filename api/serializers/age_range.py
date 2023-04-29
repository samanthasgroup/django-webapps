from rest_framework import serializers

from api.models import AgeRange


class AgeRangeSerializer(serializers.ModelSerializer[AgeRange]):
    class Meta:
        model = AgeRange
        fields = "__all__"


class AgeRangeStringSerializer(serializers.ModelSerializer[AgeRange]):
    """Serializer returns a string representation of an age range without type."""

    class Meta:
        model = AgeRange
        fields = "__all__"

    def to_representation(self, value: AgeRange) -> str:
        return f"{value.age_from}-{value.age_to}"
