from django.db import models
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from api.models import Group
from api.serializers import PublicGroupSerializer, PublicGroupWithStudentsSerializer


class PublicGroupViewSet(viewsets.ReadOnlyModelViewSet[Group]):
    """
    Public viewset for groups. Used for public API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()

    def get_serializer_class(self) -> type[BaseSerializer[Group]]:
        if self.action == "list":
            return PublicGroupSerializer
        if self.action == "retrieve":
            return PublicGroupWithStudentsSerializer

        raise NotImplementedError(f"Unknown action: {self.action}")
