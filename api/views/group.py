from typing import Any

from django.db import models
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.filters import GroupFilter
from api.models import Group
from api.processors import GroupProcessor
from api.serializers import (
    GroupWriteSerializer,
    PublicGroupSerializer,
    PublicGroupWithStudentsSerializer,
)


class PublicGroupViewSet(viewsets.ReadOnlyModelViewSet[Group], CreateModelMixin):
    """
    Public viewset for groups. Used for public API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter

    def get_serializer_class(self) -> type[BaseSerializer[Group]]:
        if self.action == "list":
            return PublicGroupSerializer
        if self.action == "retrieve":
            return PublicGroupWithStudentsSerializer
        if self.action == "create":
            return GroupWriteSerializer

        raise NotImplementedError(f"Unknown action: {self.action}")

    @action(detail=True, methods=["post"])
    def start(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        group = self.get_object()
        GroupProcessor.start(group)
        # TODO actually group gets created earlier, so maybe status 200 OK is better here
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def abort(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        group = self.get_object()
        GroupProcessor.abort(group)
        return Response(status=status.HTTP_200_OK)

    def create(self, request: Request, *args: tuple[Any], **kwargs: dict[str, Any]) -> Response:
        response = super().create(request, *args, **kwargs)
        group = Group.objects.get(id=response.data["id"])
        GroupProcessor.create(group)
        return response
