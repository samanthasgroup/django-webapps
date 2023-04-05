from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import EnrollmentTestFilter
from api.models import EnrollmentTest, EnrollmentTestResult
from api.serializers import EnrollmentTestResultSerializer, EnrollmentTestSerializer


class EnrollmentTestViewSet(ReadOnlyModelViewSet[EnrollmentTest]):
    queryset = EnrollmentTest.objects.all()
    serializer_class = EnrollmentTestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EnrollmentTestFilter


class EnrollmentTestResultViewSet(ModelViewSet[EnrollmentTestResult]):
    queryset = EnrollmentTestResult.objects.all()
    serializer_class = EnrollmentTestResultSerializer
