from rest_framework import viewsets

from api.models import TeacherUnder18
from api.serializers import TeacherUnder18Serializer


class TeacherUnder18ViewSet(viewsets.ModelViewSet):
    queryset = TeacherUnder18.objects.all()
    serializer_class = TeacherUnder18Serializer
