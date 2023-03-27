from rest_framework import viewsets

from api.models import Teacher
from api.serializers import TeacherReadSerializer, TeacherWriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class TeacherViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Teacher]):  # type: ignore
    """Teacher viewset."""

    queryset = Teacher.objects.all()
    serializer_read_class = TeacherReadSerializer
    serializer_write_class = TeacherWriteSerializer
