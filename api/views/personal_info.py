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
        Check if a personal info exists.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status.HTTP_200_OK)
