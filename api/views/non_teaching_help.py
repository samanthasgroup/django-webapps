from rest_framework import viewsets

from api.models import NonTeachingHelp
from api.serializers import NonTeachingHelpSerializer


class NonTeachingHelpViewSet(viewsets.ReadOnlyModelViewSet[NonTeachingHelp]):
    queryset = NonTeachingHelp.objects.all()
    serializer_class = NonTeachingHelpSerializer
