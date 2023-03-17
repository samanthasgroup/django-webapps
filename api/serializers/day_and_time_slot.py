from rest_framework import serializers

from api.models import DayAndTimeSlot, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = "__all__"


class DayAndTimeSlotSerializer(serializers.ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = DayAndTimeSlot
        fields = "__all__"
