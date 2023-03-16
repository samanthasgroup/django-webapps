from rest_framework import viewsets

from api.models import PersonalInfo
from api.serializers import PersonalInfoSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer
