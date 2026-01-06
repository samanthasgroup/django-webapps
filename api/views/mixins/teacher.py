from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.processors.teacher import TeacherProcessor


class TeacherReturnedFromLeaveMixin:
    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
        },
    )
    @action(detail=True, methods=["post"])
    def returned_from_leave(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        teacher = self.get_object()  # type: ignore
        TeacherProcessor.returned_from_leave(teacher)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherWentOnLeaveMixin:
    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="Action is taken"),
        },
    )
    @action(detail=True, methods=["post"])
    def went_on_leave(self, request: Request, personal_info_id: int) -> Response:  # noqa: ARG002
        teacher = self.get_object()  # type: ignore
        TeacherProcessor.went_on_leave(teacher)
        return Response(status=status.HTTP_204_NO_CONTENT)
