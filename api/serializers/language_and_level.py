from rest_framework import serializers

from api.models import LanguageAndLevel


class LanguageAndLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageAndLevel
        fields = "__all__"
