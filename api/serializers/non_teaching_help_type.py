from rest_framework import serializers

from api.models import NonTeachingHelpType


class NonTeachingHelpTypeSerializer(serializers.ModelSerializer[NonTeachingHelpType]):
    class Meta:
        model = NonTeachingHelpType
        fields = "__all__"
