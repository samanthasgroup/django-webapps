from rest_framework import viewsets

from api.filters import StudentFilter
from api.models import Student
from api.serializers import (
    DashboardStudentSerializer,
    DashboardStudentWithPersonalInfoSerializer,
    StudentReadSerializer,
    StudentWriteSerializer,
)
from api.views.mixins import ReadWriteSerializersMixin


class StudentViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Student]):  # type: ignore
    """Student viewset. Used by bot."""

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_read_class = StudentReadSerializer
    serializer_write_class = StudentWriteSerializer


class DashboardStudentViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student dashboard viewset. Used for dashboard API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = DashboardStudentSerializer


class DashboardStudentWithPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student dashboard viewset with personal info. Used for dashboard API (Tooljet).
    """

    # TODO permissions?
    # TODO test this API
    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = DashboardStudentWithPersonalInfoSerializer
    filterset_class = StudentFilter
