from rest_framework import viewsets

from api.models import Student
from api.serializers import StudentReadSerializer, StudentWriteSerializer
from api.views.mixins import ReadWriteSerializersMixin


class StudentViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Student]):
    queryset = Student.objects.all()
    serializer_read_class = StudentReadSerializer
    serializer_write_class = StudentWriteSerializer
