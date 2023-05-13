from rest_framework import viewsets

from api.models import Teacher
from api.serializers import PublicTeacherSerializer, TeacherReadSerializer, TeacherWriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class TeacherViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Teacher]):  # type: ignore
    """Teacher viewset."""

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_read_class = TeacherReadSerializer
    serializer_write_class = TeacherWriteSerializer


class PublicTeacherViewSet(viewsets.ReadOnlyModelViewSet[Teacher]):
    """
    Teacher public viewset. Used for public API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_class = PublicTeacherSerializer
