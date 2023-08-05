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


class MinifiedLanguageAndLevelSerializer(serializers.ModelSerializer[LanguageAndLevel]):
    """Represents LanguageAndLevel using Language name and Level id, not as a nested object."""

    language = serializers.CharField(source="language.name")
    level = serializers.CharField(source="level.id")

    class Meta:
        model = LanguageAndLevel
        fields = ("id", "language", "level")
