from rest_framework import viewsets

from api.models import (
    CoordinatorLogEvent,
    GroupLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
    TeacherUnder18LogEvent,
)
from api.serializers.log_event import (
    CoordinatorLogEventReadSerializer,
    CoordinatorLogEventWriteSerializer,
    GroupLogEventReadSerializer,
    GroupLogEventWriteSerializer,
    StudentLogEventReadSerializer,
    StudentLogEventWriteSerializer,
    TeacherLogEventReadSerializer,
    TeacherLogEventWriteSerializer,
    TeacherUnder18LogEventReadSerializer,
    TeacherUnder18LogEventWriteSerializer,
)
from api.views.mixins import ReadWriteSerializersMixin


class CoordinatorLogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[CoordinatorLogEvent]
):
    """Coordinator log event viewset."""

    queryset = CoordinatorLogEvent.objects.all()
    serializer_read_class = CoordinatorLogEventReadSerializer
    serializer_write_class = CoordinatorLogEventWriteSerializer


class GroupLogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[GroupLogEvent]
):
    """Group log event viewset."""

    queryset = GroupLogEvent.objects.all()
    serializer_read_class = GroupLogEventReadSerializer
    serializer_write_class = GroupLogEventWriteSerializer


class StudentLogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[StudentLogEvent]
):
    """Student log event viewset."""

    queryset = StudentLogEvent.objects.all()
    serializer_read_class = StudentLogEventReadSerializer
    serializer_write_class = StudentLogEventWriteSerializer


class TeacherLogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[TeacherLogEvent]
):
    """Adult teacher log event viewset."""

    queryset = TeacherLogEvent.objects.all()
    serializer_read_class = TeacherLogEventReadSerializer
    serializer_write_class = TeacherLogEventWriteSerializer


class TeacherUnder18LogEventViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[TeacherUnder18LogEvent]
):
    """Young teacher log event viewset."""

    queryset = TeacherUnder18LogEvent.objects.all()
    serializer_read_class = TeacherUnder18LogEventReadSerializer
    serializer_write_class = TeacherUnder18LogEventWriteSerializer
