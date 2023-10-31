from typing import Any

from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Coordinator
from api.processors.coordinator import CoordinatorProcessor
from api.serializers.coordinator import CoordinatorWriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class CoordinatorViewSet(  # type: ignore
    ReadWriteSerializersMixin,
    GenericViewSet[Coordinator],
    CreateModelMixin,
):
    """Coordinator viewset. Used by bot."""

    lookup_field = "personal_info_id"
    serializer_write_class = CoordinatorWriteSerializer

    def create(self, request: Request, *args: tuple[Any], **kwargs: dict[str, Any]) -> Response:
        response = super().create(request, *args, **kwargs)
        coordinator = Coordinator.objects.get(personal_info__id=response.data["personal_info"])
        CoordinatorProcessor.create(coordinator)
        return response
