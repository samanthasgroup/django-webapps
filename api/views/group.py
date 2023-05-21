from django.db import models
from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.filters import GroupFilter
from api.models import Group
from api.serializers import PublicGroupSerializer


class PublicGroupViewSet(viewsets.ReadOnlyModelViewSet[Group]):
    """
    Public viewset for groups. Used for public API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()
    serializer_class = PublicGroupSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter
