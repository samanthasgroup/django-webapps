from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.filters import StudentFilter
from api.models import Student
from api.processors import StudentProcessor
from api.serializers import (
    DashboardStudentMissedClassSerializer,
    DashboardStudentSerializer,
    DashboardStudentTransferSerializer,
    DashboardStudentWithPersonalInfoSerializer,
    StudentReadSerializer,
    StudentWriteSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.views.mixins import ReadWriteSerializersMixin


class StudentViewSet(ReadWriteSerializersMixin, viewsets.ModelViewSet[Student]):  # type: ignore
    """Student viewset. Used by bot."""

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_read_class = StudentReadSerializer
    serializer_write_class = StudentWriteSerializer


class DashboardStudentViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student dashboard viewset. Used for dashboard API (Tooljet).
    """

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = DashboardStudentSerializer

    @extend_schema(
        request=DashboardStudentTransferSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Student is transferred"),
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
        student = self.get_object()
        query_params_serializer = DashboardStudentTransferSerializer(
            data=request.data, instance=student
        )
        query_params_serializer.is_valid(raise_exception=True)
        StudentProcessor.transfer(
            student,
            query_params_serializer.validated_data["to_group"],
            query_params_serializer.validated_data["from_group"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=DashboardStudentMissedClassSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="invalid group or student is not in the group",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def missed_class(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        student = self.get_object()
        query_params_serializer = DashboardStudentMissedClassSerializer(
            data=request.data, instance=student
        )
        query_params_serializer.is_valid(raise_exception=True)
        StudentProcessor.missed_class(
            student,
            query_params_serializer.validated_data["group"],
            query_params_serializer.validated_data["notified"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
        },
    )
    @action(detail=True, methods=["post"])
    def went_on_leave(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        student = self.get_object()
        StudentProcessor.went_on_leave(student)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardStudentWithPersonalInfoViewSet(viewsets.ReadOnlyModelViewSet[Student]):
    """
    Student dashboard viewset with personal info. Used for dashboard API (Tooljet).
    """

    # TODO permissions?
    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_class = DashboardStudentWithPersonalInfoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudentFilter
