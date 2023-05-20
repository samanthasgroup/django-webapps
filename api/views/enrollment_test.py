from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.filters import EnrollmentTestFilter
from api.models import EnrollmentTest, EnrollmentTestResult
from api.serializers import EnrollmentTestResultCreateSerializer, EnrollmentTestSerializer
from api.serializers.enrollment_test import EnrollmentTestResultLevelSerializer


class EnrollmentTestViewSet(ReadOnlyModelViewSet[EnrollmentTest]):
    queryset = EnrollmentTest.objects.all()
    serializer_class = EnrollmentTestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EnrollmentTestFilter


class EnrollmentTestResultViewSet(CreateModelMixin, GenericViewSet[EnrollmentTestResult]):
    queryset = EnrollmentTestResult.objects.all()

    def get_serializer_class(self) -> type[BaseSerializer[EnrollmentTestResult]]:
        if self.action == "get_level":
            return EnrollmentTestResultLevelSerializer
        return EnrollmentTestResultCreateSerializer

    @action(detail=False, methods=["post"])
    def get_level(self, request: Request) -> Response:
        """Calculates level of language based on number of correct answers."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
