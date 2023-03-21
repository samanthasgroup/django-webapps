from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.filters import AgeRangeFilter
from api.models import AgeRange
from api.serializers import AgeRangeSerializer


class AgeRangeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgeRange.objects.all()
    serializer_class = AgeRangeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AgeRangeFilter
