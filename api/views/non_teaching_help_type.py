from rest_framework import viewsets

from api.models import NonTeachingHelpType
from api.serializers import NonTeachingHelpTypeSerializer


class NonTeachingHelpTypeViewSet(viewsets.ReadOnlyModelViewSet[NonTeachingHelpType]):
    queryset = NonTeachingHelpType.objects.all()
    serializer_class = NonTeachingHelpTypeSerializer
