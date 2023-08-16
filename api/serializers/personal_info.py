from typing import Any

from rest_framework import serializers

from api.exceptions import ConflictError, NotAcceptableError
from api.models import PersonalInfo
from api.utils import capitalize_each_word


class PersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    class Meta:
        model = PersonalInfo
        fields = "__all__"


class CheckNameAndEmailExistenceSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to check if user with given name and email exists in database.

    This serializer assumes that a client is trying to create an instance of PersonalInfo
    and hence raises 409 error if an entry with the given data already exists.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        prepared_attrs = {
            attr: capitalize_each_word(attrs[attr]) for attr in ("first_name", "last_name")
        }
        prepared_attrs["email"] = attrs["email"].lower()

        if PersonalInfo.objects.filter(**prepared_attrs).exists():
            raise ConflictError
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
        raise NotAcceptableError

    class Meta:
        model = PersonalInfo
        fields = ("registration_telegram_bot_chat_id",)
        extra_kwargs = {"registration_telegram_bot_chat_id": {"required": True}}


class DashboardPersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    """
    A serializer used to return information about a person in dashboard (Tooljet) views.
    The data returned is nested inside a parent entity (teacher or student),
    so fields like id and name are not returned here.
    """

    class Meta:
        model = PersonalInfo
        fields = (
            "email",
            "chatwoot_conversation_id",
            "phone",
            "registration_telegram_bot_chat_id",
            "telegram_username",
        )


class DashboardStandalonePersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    """
    Used in the Tooljet dashboard to identify a coordinator by their email.
    Returns minimal data.
    """

    class Meta:
        model = PersonalInfo
        fields = (
            "id",
            "email",
        )
        read_only_fields = fields
