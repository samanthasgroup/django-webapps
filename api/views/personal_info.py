from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.serializers import ValidationError as RestValidationError

from api.exceptions import ConflictError
from api.filters import PersonalInfoFilter
from api.filters.personal_info import DashboardPersonalInfoFilter
from api.models import PersonalInfo
from api.serializers import (
    CheckChatIdExistenceSerializer,
    CheckNameAndEmailExistenceSerializer,
    PersonalInfoSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.serializers.personal_info import DashboardMinifiedPersonalInfoSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet[PersonalInfo]):
    """Personal info viewset. Used by bot."""

    queryset = PersonalInfo.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonalInfoFilter

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
        try:
            serializer.is_valid(raise_exception=True)
        # ошибка при валидации полей модели
        except RestValidationError as e:
            error_detail = e.detail
            if (
                isinstance(error_detail, dict)
                and "non_field_errors" in error_detail
                and any(error_detail["non_field_errors"])
            ):
                return Response(
                    {"detail": "Personal info already exists"}, status=status.HTTP_409_CONFLICT
                )
            raise  # Если ошибка не связана с уникальностью, пробрасываем дальше
        # кастомная ошибка при дубилровании записи
        except ConflictError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        return Response({"detail": "Personal info does not exist"}, status=status.HTTP_200_OK)

    def get_serializer_class(self) -> type[BaseSerializer[PersonalInfo]]:
        if self.action == "check_existence":
            return CheckNameAndEmailExistenceSerializer
        if self.action == "check_existence_of_chat_id":
            return CheckChatIdExistenceSerializer
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


class DashboardPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[PersonalInfo]):
    queryset = PersonalInfo.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DashboardPersonalInfoFilter
    serializer_class = DashboardMinifiedPersonalInfoSerializer
