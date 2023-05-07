from typing import Any

from rest_framework import serializers

from api.models import PersonalInfo


class PersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    class Meta:
        model = PersonalInfo
        fields = "__all__"


class PersonalInfoCheckExistenceSerializer(serializers.ModelSerializer[PersonalInfo]):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if PersonalInfo.objects.filter(**attrs).exists():
            # TODO: Discuss errors format.
            raise serializers.ValidationError("User with this information already exists.")
        return attrs


class CheckNameAndEmailExistenceSerializer(PersonalInfoCheckExistenceSerializer):
    class Meta:
        model = PersonalInfo
        fields = ["first_name", "last_name", "email"]


class CheckChatIdExistenceSerializer(PersonalInfoCheckExistenceSerializer):
    """A serializer used to check if chat ID from telegram registration bot exists in database."""

    class Meta:
        model = PersonalInfo
        fields = ["registration_telegram_bot_chat_id"]
