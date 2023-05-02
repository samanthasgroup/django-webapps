from rest_framework import serializers

from api.models import Coordinator


class MinifiedCoordinatorSerializer(serializers.ModelSerializer[Coordinator]):
    """Serializer for Coordinator model with only id and full_name fields."""

    full_name = serializers.CharField(source="personal_info.full_name")
    id = serializers.IntegerField(source="personal_info_id")

    class Meta:
        model = Coordinator
        fields = ("id", "full_name")
