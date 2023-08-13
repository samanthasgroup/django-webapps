from django.db import models
from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.exceptions import ConflictError
from api.filters import GroupFilter
from api.models import Group
from api.models.auxil.constants import GroupDiscardReason
from api.models.choices.status import GroupProjectStatus
from api.processors import GroupProcessor
from api.serializers import (
    DashboardGroupSerializer,
    DashboardGroupWithStudentsSerializer,
    GroupDiscardSerializer,
    GroupReadSerializer,
    GroupWriteSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.views.mixins import CreateGroupMixin, ReadWriteSerializersMixin


class GroupViewSet(  # type: ignore
    ReadWriteSerializersMixin, CreateGroupMixin, viewsets.ModelViewSet[Group]
):
    """Internal group viewset. Used by bot."""

    queryset = Group.objects.all()
    serializer_read_class = GroupReadSerializer
    serializer_write_class = GroupWriteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter


class DashboardGroupViewSet(viewsets.ReadOnlyModelViewSet[Group], CreateGroupMixin):
    """
    Dashboard viewset for groups. Used for dashboard API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="discard_reason",
                type=str,
                enum=[e.value for e in GroupDiscardReason],
                required=True,
            )
        ],
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Group is discarded"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Group is not in the pending state",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the data",
            ),
        },
    )
    @action(detail=True, methods=["delete"])
    def discard(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        group = self.get_object()
        if group.project_status != GroupProjectStatus.PENDING:
            raise ConflictError("Group is not in the pending state")
        query_params_serializer = GroupDiscardSerializer(data=request.query_params)
        query_params_serializer.is_valid(raise_exception=True)
        GroupProcessor.discard(group, query_params_serializer.validated_data["discard_reason"])
        return Response(status=status.HTTP_204_NO_CONTENT)
