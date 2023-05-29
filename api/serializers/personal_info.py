from typing import Any

from rest_framework import serializers

from api.models import PersonalInfo


class PersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    class Meta:
        model = PersonalInfo
        fields = "__all__"


class CheckNameAndEmailExistenceSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to check if user with given name and email exists in database.

    This serializer assumes that a client is trying to create an instance of PersonalInfo
    and hence raises 400 error if an entry with the given data already exists.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if PersonalInfo.objects.filter(**attrs).exists():
            # TODO: Discuss errors format.
            raise serializers.ValidationError("User with this information already exists.")
        return attrs

    class Meta:
        model = PersonalInfo
        fields = ("first_name", "last_name", "email")


class CheckChatIdExistenceSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to check if chat ID from telegram registration bot exists in database.

    Since it is impossible to create a `PersonalInfo` item without a name and an email,
    this serializer is supposed to be used with GET requests.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if PersonalInfo.objects.filter(**attrs).exists():
            return attrs
        raise serializers.ValidationError(f"No user with {attrs=} was found.")

    class Meta:
        model = PersonalInfo
        fields = ("registration_telegram_bot_chat_id",)
        extra_kwargs = {"registration_telegram_bot_chat_id": {"required": True}}


class PublicPersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to return public information about a user in Tooljet views."""

    class Meta:
        model = PersonalInfo
        fields = (
            "email",
            "chatwoot_conversation_id",
            "phone",
            "registration_telegram_bot_chat_id",
            "telegram_username",
        )
