from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.models import PersonalInfo
from api.serializers import (
    CheckChatIdExistenceSerializer,
    CheckNameAndEmailExistenceSerializer,
    PersonalInfoSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet[PersonalInfo]):
    queryset = PersonalInfo.objects.all()

    @extend_schema(
        responses={
            status.HTTP_200_OK: PersonalInfoSerializer,
            status.HTTP_409_CONFLICT: BaseAPIExceptionSerializer,
            status.HTTP_400_BAD_REQUEST: ValidationErrorSerializer,
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
        if self.action == "check_existence":
            return CheckNameAndEmailExistenceSerializer
        if self.action == "check_existence_of_chat_id":
            return CheckChatIdExistenceSerializer
        return PersonalInfoSerializer

    @extend_schema(parameters=[CheckChatIdExistenceSerializer])
    @action(detail=False, methods=["get"])
    def check_existence_of_chat_id(self, request: Request) -> Response:
        """
        Checks if `PersonalInfo` with given ``registration_telegram_bot_chat_id`` exists.

        Method GET is used because one cannot create a `PersonalInfo` instance with just chat ID.
        """

        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(request.query_params)
