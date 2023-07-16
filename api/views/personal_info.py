from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.exceptions import NotAcceptableError
from api.models import PersonalInfo
from api.serializers import (
    CheckChatIdExistenceSerializer,
    CheckNameAndEmailExistenceSerializer,
    PersonalInfoSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="registration_telegram_bot_chat_id",
            location=OpenApiParameter.QUERY,
            type=int,
            description="Filter by chat ID in Telegram registration bot",
        )
    ],
    responses={
        status.HTTP_200_OK: OpenApiResponse(
            response=PersonalInfoSerializer, description="Returns personal info records."
        ),
        status.HTTP_406_NOT_ACCEPTABLE: OpenApiResponse(
            response=BaseAPIExceptionSerializer,
            description="No personal info records were found that match given params.",
        ),
    },
)
class PersonalInfoViewSet(viewsets.ModelViewSet[PersonalInfo]):
    def get_queryset(self) -> QuerySet[PersonalInfo]:
        """Optionally restricts the returned personal info items to records
        with given chat ID in Telegram registration bot.
        """
        queryset: QuerySet[PersonalInfo] = PersonalInfo.objects.all()
        chat_id = self.request.query_params.get("registration_telegram_bot_chat_id")
        if chat_id is not None:
            queryset = queryset.filter(registration_telegram_bot_chat_id=chat_id)

        if not queryset.exists():
            # To be consistent with similar views, it's better to raise 406 rather than
            # return 200 with empty list
            raise NotAcceptableError

        return queryset

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
