from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from api.models import Coordinator
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
