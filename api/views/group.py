from django.db import models
from rest_framework import viewsets

from api.models import Group
from api.serializers import PublicGroupSerializer


class PublicGroupViewSet(viewsets.ReadOnlyModelViewSet[Group]):
    """
    Group public viewset. Used for public API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()
    serializer_class = PublicGroupSerializer
