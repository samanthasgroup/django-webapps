from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.models import PersonalInfo
from api.serializers import PersonalInfoCheckExistenceSerializer, PersonalInfoSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet[PersonalInfo]):
    queryset = PersonalInfo.objects.all()

    def get_serializer_class(self) -> type[BaseSerializer[PersonalInfo]]:
        if self.action == "check_existence":
            return PersonalInfoCheckExistenceSerializer
        return PersonalInfoSerializer

    @action(detail=False, methods=["post"])
    def check_existence(self, request: Request) -> Response:
        """
        Checks if a personal info exists.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status.HTTP_200_OK)

    @extend_schema(
        description=(
            "Checks if personal info exists with this chat ID of Telegram registration bot."
        ),
        parameters=[
            OpenApiParameter(name="chat_id", type=str, required=True),
        ],
        responses={
            200: OpenApiResponse(description="Chat ID is found"),
            404: OpenApiResponse(description="Chat ID not found"),
        },
    )
    @action(detail=False, methods=["get"])
    def check_existence_of_chat_id(self, request: Request) -> Response:
        """
        Check if PersonalInfo with given ``registration_telegram_bot_chat_id`` exists.
        """
        # This method is used without a serializer because this seems to be overkill
        # for a simple GET request with a single parameter.  Since name and e-mail are required
        # fields for PersonalInfo (and we only have chat ID), we cannot use the same technique
        # as in .check_existence(). Note that .check_existence() above returns 200 OK if the
        # personal info does NOT exist and 400 BAD REQUEST if it DOES exist.
        # This is because POST method is used up there, so non-existent user can be "created",
        # hence success is reported if no user was found.
        # Here we use GET and the responses are different.

        if PersonalInfo.objects.filter(
            registration_telegram_bot_chat_id=request.GET.get("chat_id")
        ).exists():
            return Response(status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)
