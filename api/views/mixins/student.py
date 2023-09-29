from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.processors import StudentProcessor


class StudentReturnedFromLeaveMixin:
    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
        },
    )
    @action(detail=True, methods=["post"])
    def returned_from_leave(
        self, request: Request, personal_info_id: int  # noqa: ARG002
    ) -> Response:
        student = self.get_object()  # type: ignore
        StudentProcessor.returned_from_leave(student)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentWentOnLeaveMixin:
    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
        },
    )
    @action(detail=True, methods=["post"])
    def went_on_leave(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        student = self.get_object()  # type: ignore
        StudentProcessor.went_on_leave(student)
        return Response(status=status.HTTP_204_NO_CONTENT)
