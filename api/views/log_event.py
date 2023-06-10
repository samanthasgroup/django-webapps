from rest_framework import viewsets

from api.models import CoordinatorLogEvent
from api.serializers.log_event import (
    CoordinatorLogEventReadSerializer,
    CoordinatorLogEventWriteSerializer,
)
from api.views.mixins import ReadWriteSerializersMixin


class CoordinatorLogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[CoordinatorLogEvent]
):
    """Coordinator log event viewset."""

    queryset = CoordinatorLogEvent.objects.all()
    serializer_read_class = CoordinatorLogEventReadSerializer
    serializer_write_class = CoordinatorLogEventWriteSerializer
