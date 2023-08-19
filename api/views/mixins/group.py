from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import Group
from api.processors import GroupProcessor
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.serializers.group.internal import GroupDiscardSerializer


class CreateGroupMixin(CreateModelMixin):
    """Mixin for group creation. Shared between dashboard and internal router"""

    def create(self, request: Request, *args: tuple[Any], **kwargs: dict[str, Any]) -> Response:
        response = super().create(request, *args, **kwargs)
        group = Group.objects.get(id=response.data["id"])
        GroupProcessor.create(group)
        return response


class DiscardGroupMixin:
    @extend_schema(
        parameters=[GroupDiscardSerializer],
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
        group = self.get_object()  # type: ignore
        query_params_serializer = GroupDiscardSerializer(instance=group, data=request.query_params)
        query_params_serializer.is_valid(raise_exception=True)
        GroupProcessor.discard(group, query_params_serializer.validated_data["discard_reason"])
        return Response(status=status.HTTP_204_NO_CONTENT)
