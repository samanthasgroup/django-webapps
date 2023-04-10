from django_filters import rest_framework as filters
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.filters import EnrollmentTestFilter
from api.models import EnrollmentTest, EnrollmentTestResult
from api.serializers import EnrollmentTestResultCreateSerializer, EnrollmentTestSerializer


class EnrollmentTestViewSet(ReadOnlyModelViewSet[EnrollmentTest]):
    queryset = EnrollmentTest.objects.all()
    serializer_class = EnrollmentTestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EnrollmentTestFilter


class EnrollmentTestResultViewSet(CreateModelMixin, GenericViewSet[EnrollmentTestResult]):
    queryset = EnrollmentTestResult.objects.all()
    serializer_class = EnrollmentTestResultCreateSerializer
