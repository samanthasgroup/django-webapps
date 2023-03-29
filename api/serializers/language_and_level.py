from rest_framework import serializers

from api.models import Language, LanguageAndLevel


class LanguageSerializer(serializers.ModelSerializer[Language]):
    class Meta:
        model = Language
        fields = "__all__"


class LanguageAndLevelSerializer(serializers.ModelSerializer[LanguageAndLevel]):
    language = LanguageSerializer()

    class Meta:
        model = LanguageAndLevel
        fields = "__all__"
