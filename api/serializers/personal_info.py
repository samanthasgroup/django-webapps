from collections import OrderedDict
from typing import Any, cast

from django.db.models import QuerySet
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


class GetChatwootConversationIdSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to look up Chatwoot conversation ID by Telegram bot chat ID."""

    chatwoot_conversation_id = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.personal_info_with_this_telegram_chat_id: QuerySet[PersonalInfo] | None = None

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        personal_info = PersonalInfo.objects.filter(**attrs)
        if personal_info.exists():
            self.personal_info_with_this_telegram_chat_id = personal_info
            return attrs
        raise NotAcceptableError

    class Meta:
        model = PersonalInfo
        fields = ("registration_telegram_bot_chat_id", "chatwoot_conversation_id")
        extra_kwargs = {
            "registration_telegram_bot_chat_id": {"required": True, "write_only": True}
        }

    def get_chatwoot_conversation_id(self, _: OrderedDict[str, Any]) -> int | None:
        return cast(
            int,
            self.personal_info_with_this_telegram_chat_id.first().chatwoot_conversation_id,  # type:ignore[union-attr]  # noqa:E501
        )


class PublicPersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    """A serializer used to return public information about a person in Tooljet views."""

    class Meta:
        model = PersonalInfo
        fields = (
            "email",
            "chatwoot_conversation_id",
            "phone",
            "registration_telegram_bot_chat_id",
            "telegram_username",
        )
