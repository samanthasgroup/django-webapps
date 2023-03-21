from rest_framework import viewsets

from api.models import LanguageAndLevel
from api.serializers import LanguageAndLevelSerializer


class LanguageAndLevelViewSet(viewsets.ReadOnlyModelViewSet[LanguageAndLevel]):
    queryset = LanguageAndLevel.objects.all()
    serializer_class = LanguageAndLevelSerializer
