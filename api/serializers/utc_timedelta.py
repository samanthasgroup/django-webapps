import datetime

from rest_framework import serializers


class UTCTimedeltaField(serializers.Field):  # type: ignore
    """Read-only field that returns a string representation of a UTC timedelta."""

    def to_representation(self, value: datetime.timedelta) -> str:
        hours, remain_minutes_seconds = divmod(int(value.total_seconds()), 3600)
        minutes = remain_minutes_seconds // 60
        sign = "+" if hours >= 0 else "-"
        return f"UTC{sign}{abs(hours):02}:{minutes:02}"
