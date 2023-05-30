from django.db.models import Count, Prefetch
from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.filters import TeacherFilter
from api.models import Group, Teacher
from api.serializers import (
    PublicTeacherSerializer,
    PublicTeacherWithPersonalInfoSerializer,
    TeacherReadSerializer,
    TeacherWriteSerializer,
)
from api.views.mixins import ReadWriteSerializersMixin


class TeacherViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Teacher]):  # type: ignore
    """Teacher viewset."""

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_read_class = TeacherReadSerializer
    serializer_write_class = TeacherWriteSerializer


class PublicTeacherViewSet(viewsets.ReadOnlyModelViewSet[Teacher]):
    """
    Teacher public viewset. Used for public API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_class = PublicTeacherSerializer


class PublicTeacherWithPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[Teacher]):
    """
    Teacher public viewset with personal info. Used for public API (Tooljet).
    """

    # TODO permissions?
    # TODO test this API
    lookup_field = "personal_info_id"
    queryset = Teacher.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.annotate(students_count=Count("students"))),
    ).all()
    serializer_class = PublicTeacherWithPersonalInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TeacherFilter
