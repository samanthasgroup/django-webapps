from django.db.models import Count, Prefetch
from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.filters import TeacherFilter
from api.models import Group, Teacher
from api.processors.teacher import TeacherProcessor
from api.serializers import (
    DashboardTeacherSerializer,
    DashboardTeacherTransferSerializer,
    DashboardTeacherWithPersonalInfoSerializer,
    TeacherReadSerializer,
    TeacherWriteSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.views.mixins import (
    ReadWriteSerializersMixin,
    TeacherReturnedFromLeaveMixin,
    TeacherWentOnLeaveMixin,
)


class TeacherViewSet(  # type: ignore
    ReadWriteSerializersMixin,
    viewsets.ModelViewSet[Teacher],
    TeacherReturnedFromLeaveMixin,
    TeacherWentOnLeaveMixin,
):
    """Teacher viewset. Used by bot."""

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_read_class = TeacherReadSerializer
    serializer_write_class = TeacherWriteSerializer


class DashboardTeacherViewSet(
    viewsets.ReadOnlyModelViewSet[Teacher], TeacherWentOnLeaveMixin, TeacherReturnedFromLeaveMixin
):
    """
    Teacher dashboard viewset. Used for dashboard API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Teacher.objects.all()
    serializer_class = DashboardTeacherSerializer

    @extend_schema(
        request=DashboardTeacherTransferSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Teacher is transferred"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Transfer group is not found",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def transfer(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        teacher = self.get_object()
        query_params_serializer = DashboardTeacherTransferSerializer(
            data=request.data, instance=teacher
        )
        query_params_serializer.is_valid(raise_exception=True)
        TeacherProcessor.transfer(
            teacher,
            query_params_serializer.validated_data["to_group"],
            query_params_serializer.validated_data["from_group"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardTeacherWithPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[Teacher]):
    """
    Teacher dashboard viewset with personal info. Used for dashboard API (Tooljet).
    """

    # TODO permissions?
    # TODO test this API
    lookup_field = "personal_info_id"
    queryset = Teacher.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.annotate(students_count=Count("students"))),
    ).all()
    serializer_class = DashboardTeacherWithPersonalInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TeacherFilter
