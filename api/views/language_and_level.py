from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.filters import LanguageAndLevelFilter
from api.models import LanguageAndLevel
from api.serializers import LanguageAndLevelSerializer


class LanguageAndLevelViewSet(viewsets.ReadOnlyModelViewSet[LanguageAndLevel]):
    queryset = LanguageAndLevel.objects.all()
    serializer_class = LanguageAndLevelSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LanguageAndLevelFilter


class DashboardLanguageAndLevelViewSet(viewsets.ReadOnlyModelViewSet[LanguageAndLevel]):
    queryset = LanguageAndLevel.objects.all()
    serializer_class = LanguageAndLevelSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LanguageAndLevelFilter
