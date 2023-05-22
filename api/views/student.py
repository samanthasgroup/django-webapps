from rest_framework import viewsets

from api.models import Student
from api.serializers import PublicStudentSerializer, StudentReadSerializer, StudentWriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class StudentViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Student]):  # type: ignore
    """ViewSet for reading and writing data from/to students' table.

    After creating a student with POST, returns student's **internal ID** along with other info.
    Internal ID is needed e.g. to send the results of an enrollment test to the backend.
    """

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
