from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.models import PersonalInfo
from api.serializers import (
    CheckChatIdExistenceSerializer,
    CheckNameAndEmailExistenceSerializer,
    GetChatwootConversationIdSerializer,
    PersonalInfoSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet[PersonalInfo]):
    queryset = PersonalInfo.objects.all()

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=PersonalInfoSerializer, description="Personal info does not exist."
            ),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer, description="Personal info exists."
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the data (e.g. invalid email format)",
            ),
        }
    )
    @action(detail=False, methods=["post"])
    def check_existence(self, request: Request) -> Response:
        """
        Checks if a personal info exists.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status.HTTP_200_OK)

    def get_serializer_class(self) -> type[BaseSerializer[PersonalInfo]]:
        match self.action:
            case "check_existence":
                return CheckNameAndEmailExistenceSerializer
            case "check_existence_of_chat_id":
                return CheckChatIdExistenceSerializer
            case "get_chatwoot_conversation_id":
                return GetChatwootConversationIdSerializer
            case _:
                return PersonalInfoSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="registration_telegram_bot_chat_id", type=int, required=True),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CheckChatIdExistenceSerializer,
                description="User with this chat ID exists",
            ),
            status.HTTP_406_NOT_ACCEPTABLE: OpenApiResponse(
                response=BaseAPIExceptionSerializer, description="No user with this chat ID exists"
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the data (e.g. no chat ID was passed)",
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def check_existence_of_chat_id(self, request: Request) -> Response:
        """
        Checks if `PersonalInfo` with given ``registration_telegram_bot_chat_id`` exists.

        Method GET is used because one cannot create a `PersonalInfo` instance with just chat ID.
        """

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(request.query_params)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="registration_telegram_bot_chat_id", type=int, required=True),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=CheckChatIdExistenceSerializer,
                description="User with this chat ID exists: returning Chatwoot conversation ID",
                # the auto example will show "telegram_registration_bot_chat_id" instead of
                # "chatwoot_conversation_id", despite the actual request returning correct field
                examples=[
                    OpenApiExample(name="id_found", value={"chatwoot_conversation_id": 123})
                ],
            ),
            status.HTTP_406_NOT_ACCEPTABLE: OpenApiResponse(
                response=BaseAPIExceptionSerializer, description="No user with this chat ID exists"
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the data",
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def get_chatwoot_conversation_id(self, request: Request) -> Response:
        """Gets Chatwoot conversation ID that matches chat ID in Telegram registration bot."""

        # One Telegram account can only have one conversation with an operator
        # in Chatwoot. The registration bot can send the chat ID that it knows by definition
        # and receive the Chatwoot conversation ID if it exists. This allows to connect
        # the user with the operator via the registration bot.
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
