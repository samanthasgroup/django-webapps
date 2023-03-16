from rest_framework import serializers

from api.models import AgeRange


class AgeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeRange
        fields = "__all__"
