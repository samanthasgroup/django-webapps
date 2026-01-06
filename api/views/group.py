from django.db import models
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.filters import GroupFilter
from api.models import Group
from api.processors import GroupProcessor
from api.serializers import (
    DashboardGroupSerializer,
    DashboardGroupWithStudentsSerializer,
    GroupReadSerializer,
    GroupWriteSerializer,
)
from api.views.mixins import CreateGroupMixin, DiscardGroupMixin, ReadWriteSerializersMixin


class GroupViewSet(  # type: ignore
    ReadWriteSerializersMixin, CreateGroupMixin, DiscardGroupMixin, viewsets.ModelViewSet[Group]
):
    """Internal group viewset. Used by bot."""

    queryset = Group.objects.all()
    serializer_read_class = GroupReadSerializer
    serializer_write_class = GroupWriteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter


class DashboardGroupViewSet(viewsets.ReadOnlyModelViewSet[Group], DiscardGroupMixin, CreateGroupMixin):
    """
    Dashboard viewset for groups. Used for dashboard API (Tooljet).
    """

    queryset = Group.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter

    def get_queryset(self) -> QuerySet[Group]:
        return Group.objects.annotate(students_count=models.Count("students")).all()

    def get_serializer_class(self) -> type[BaseSerializer[Group]]:
        if self.action == "list":
            return DashboardGroupSerializer
        if self.action == "retrieve":
            return DashboardGroupWithStudentsSerializer
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

    @action(detail=True, methods=["post"])
    def confirm_ready_to_start(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        group = self.get_object()
        GroupProcessor.confirm_ready_to_start(group)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def finish(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        group = self.get_object()
        GroupProcessor.finish(group)
        return Response(status=status.HTTP_200_OK)
