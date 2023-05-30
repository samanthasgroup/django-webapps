from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.filters import StudentFilter
from api.models import Student
from api.serializers import (
    PublicStudentSerializer,
    PublicStudentWithPersonalInfoSerializer,
    StudentReadSerializer,
    StudentWriteSerializer,
)
from api.views.mixins import ReadWriteSerializersMixin


class StudentViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Student]):  # type: ignore
    """Student viewset."""

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_read_class = StudentReadSerializer
    serializer_write_class = StudentWriteSerializer


class PublicStudentViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student public viewset. Used for public API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = PublicStudentSerializer


class PublicStudentWithPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student public viewset with personal info. Used for public API (Tooljet).
    """

    # TODO permissions?
    # TODO test this API
    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = PublicStudentWithPersonalInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudentFilter
