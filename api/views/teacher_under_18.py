from rest_framework import viewsets

from api.models import TeacherUnder18
from api.serializers import TeacherUnder18ReadSerializer, TeacherUnder18WriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class TeacherUnder18ViewSet(  # type: ignore
    ReadWriteSerializersMixin, viewsets.ModelViewSet[TeacherUnder18]
):
    """TeacherUnder18 viewset."""

    queryset = TeacherUnder18.objects.all()
    serializer_read_class = TeacherUnder18ReadSerializer
    serializer_write_class = TeacherUnder18WriteSerializer
