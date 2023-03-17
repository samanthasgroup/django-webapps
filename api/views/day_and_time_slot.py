from rest_framework import viewsets

from api.models import DayAndTimeSlot
from api.serializers import DayAndTimeSlotSerializer


class DayAndTimeSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DayAndTimeSlot.objects.all()
    serializer_class = DayAndTimeSlotSerializer
