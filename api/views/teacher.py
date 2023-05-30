from django.db.models import Count, Prefetch
from rest_framework import viewsets

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
    # TODO filter by coordinator
    lookup_field = "personal_info_id"
    queryset = Teacher.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.annotate(students_count=Count("students"))),
    ).all()
    serializer_class = PublicTeacherWithPersonalInfoSerializer
