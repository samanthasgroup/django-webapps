from rest_framework import serializers

from api.models import DayAndTimeSlot, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer[TimeSlot]):
    class Meta:
        model = TimeSlot
        fields = "__all__"


class DayAndTimeSlotSerializer(serializers.ModelSerializer[DayAndTimeSlot]):
    time_slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = DayAndTimeSlot
        fields = "__all__"


class MinifiedDayAndTimeSlotSerializer(serializers.ModelSerializer[DayAndTimeSlot]):
    """Represents DayAndTimeSlot using TimeSlot fields plainly, not as a nested object."""

    from_utc_hour = serializers.TimeField(source="time_slot.from_utc_hour")
    to_utc_hour = serializers.TimeField(source="time_slot.to_utc_hour")

    class Meta:
        model = DayAndTimeSlot
        fields = ("day_of_week_index", "from_utc_hour", "to_utc_hour")
