from django.db import models
from django.http import HttpResponse, HttpResponseBadRequest
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from api.filters import GroupFilter
from api.models import Group
from api.processors.group import GroupProcessor
from api.serializers import PublicGroupSerializer, PublicGroupWithStudentsSerializer


class PublicGroupViewSet(viewsets.ReadOnlyModelViewSet[Group]):
    """
    Public viewset for groups. Used for public API (Tooljet).
    """

    queryset = Group.objects.annotate(students_count=models.Count("students")).all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter

    def get_serializer_class(self) -> type[BaseSerializer[Group]]:
        if self.action == "list":
            return PublicGroupSerializer
        if self.action == "retrieve":
            return PublicGroupWithStudentsSerializer

        raise NotImplementedError(f"Unknown action: {self.action}")

    @action(detail=True, methods=["post"])
    def start(self, request: Request) -> Response | HttpResponse:
        data = request.data
        try:
            group_id = data["id"]
        except KeyError:
            return HttpResponseBadRequest("Pass 'id' of the group in 'id' field.")

        try:
            group = Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            return HttpResponseBadRequest(f"Group with id {group_id} not found")

        GroupProcessor.start(group)
        return Response(data=data, status=status.HTTP_201_CREATED)
