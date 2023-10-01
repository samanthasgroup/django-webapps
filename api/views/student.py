from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

from api.filters import StudentFilter
from api.models import Student
from api.models.choices.status.project import StudentProjectStatus
from api.processors import StudentProcessor
from api.serializers import (
    DashboardAvailableStudentsSerializer,
    DashboardStudentMissedClassSerializer,
    DashboardStudentSerializer,
    DashboardStudentTransferSerializer,
    DashboardStudentWithPersonalInfoSerializer,
    MinifiedStudentSerializer,
    StudentReadSerializer,
    StudentWriteSerializer,
)
from api.serializers.errors import BaseAPIExceptionSerializer, ValidationErrorSerializer
from api.views.mixins import (
    ReadWriteSerializersMixin,
    StudentReturnedFromLeaveMixin,
    StudentWentOnLeaveMixin,
)


class StudentViewSet(  # type: ignore
    ReadWriteSerializersMixin,
    viewsets.ModelViewSet[Student],
    StudentWentOnLeaveMixin,
    StudentReturnedFromLeaveMixin,
):
    """Student viewset. Used by bot."""

    lookup_field = "personal_info_id"
    queryset = Student.objects.all()
    serializer_read_class = StudentReadSerializer
    serializer_write_class = StudentWriteSerializer


class DashboardStudentViewSet(
    viewsets.ReadOnlyModelViewSet[Student], StudentWentOnLeaveMixin, StudentReturnedFromLeaveMixin
):
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
        parameters=[DashboardAvailableStudentsSerializer],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ListSerializer(child=MinifiedStudentSerializer()),
                description="Students returned",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Invalid time slots",
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def available_students_list(self, request: Request) -> Response:  # noqa: ARG002
        query_params_serializer = DashboardAvailableStudentsSerializer(
            data=request.query_params,
        )
        query_params_serializer.is_valid(raise_exception=True)
        matched_students = Student.objects.filter(
            project_status=StudentProjectStatus.NO_GROUP_YET,
            availability_slots__id__in=query_params_serializer.validated_data["time_slot_ids"],
        ).distinct()
        return Response(
            data=MinifiedStudentSerializer(matched_students, many=True).data,
            status=status.HTTP_200_OK,
        )


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
