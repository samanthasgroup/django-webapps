from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

from api.exceptions import ConflictError
from api.filters import StudentFilter
from api.models import Student
from api.models.choices.status.project import StudentProjectStatus
from api.processors import StudentProcessor
from api.serializers import (
    DashboardAvailableStudentsSerializer,
    DashboardCompletedOralInterviewSerializer,
    DashboardStudentAcceptedOfferedGroupSerializer,
    DashboardStudentMissedClassSerializer,
    DashboardStudentOfferJoinGroupSerializer,
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
                description="Student is already in transfer_to group or not in transfer_from",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Group not found",
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
                description="Student is not in the group",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Group not found",
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
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def expelled(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        StudentProcessor.expelled(student)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def left_project_prematurely(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        StudentProcessor.left_project_prematurely(student)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=DashboardStudentAcceptedOfferedGroupSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Coordinator or student is not in the group",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Something is wrong with the query params",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Group not found",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def accepted_offered_group(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        query_params_serializer = DashboardStudentAcceptedOfferedGroupSerializer(
            data=request.data, instance=student
        )
        query_params_serializer.is_valid(raise_exception=True)
        StudentProcessor.accepted_offered_group(
            student,
            query_params_serializer.validated_data["coordinator"],
            query_params_serializer.validated_data["group"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Only students with no groups can be processed",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def finished_and_left(
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        if student.has_groups:
            raise ConflictError("Only students with no groups can be processed")
        StudentProcessor.finished_and_left(student)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        request=DashboardStudentOfferJoinGroupSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Student is in the group",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ValidationErrorSerializer,
                description="Something is wrong with the query params",
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Group not found",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def offer_join_group(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        query_params_serializer = DashboardStudentOfferJoinGroupSerializer(
            data=request.data, instance=student
        )
        query_params_serializer.is_valid(raise_exception=True)
        StudentProcessor.offer_join_group(
            student,
            query_params_serializer.validated_data["group"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Only students with no groups can be processed",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def put_in_waiting_queue(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        if student.has_groups:
            raise ConflictError("Only students with no groups can be processed")
        StudentProcessor.put_in_waiting_queue(student)
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
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Some of time slots not found",
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

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=ListSerializer(child=DashboardStudentSerializer()),
                description="Students returned",
            ),
        }
    )
    @action(detail=False, methods=["get"])
    def active_students_with_no_groups(self, request: Request) -> Response:  # noqa: ARG002
        matched_students = Student.objects.filter(
            project_status=StudentProjectStatus.STUDYING
        ).filter_has_no_groups()
        return Response(
            data=DashboardStudentSerializer(matched_students, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DashboardCompletedOralInterviewSerializer,
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
            status.HTTP_409_CONFLICT: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description='Student status must be "needs_interview_to_determine_level"',
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                response=BaseAPIExceptionSerializer,
                description="Language and level is not found",
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def completed_oral_interview(  # noqa: ARG002
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()
        if student.project_status != StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL:
            raise ConflictError(
                "Only with status NEEDS_INTERVIEW_TO_DETERMINE_LEVEL can be processed"
            )
        data_serializer = DashboardCompletedOralInterviewSerializer(data=request.data)
        data_serializer.is_valid(raise_exception=True)
        StudentProcessor.completed_oral_interview(
            student, data_serializer.validated_data["language_and_level"]
        )
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
