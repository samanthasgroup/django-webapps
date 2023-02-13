from django.db import models

from api.models.aux import MultilingualModel


class DayOfWeek(MultilingualModel):
    """Model for days of the week (with internationalization)."""

    # We could just use numbers and then localize them using Babel,
    # but it seems easier to just create a table with 7 rows.


class TimeSlot(models.Model):
    # Postgres supports ranges, and in Django we could use IntegerRangeField for a Postgres range,
    # but that would hinder development and testing with SQLite.
    # Also, Postgres has no pure time ranges (only date-time).
    from_utc_hour = models.TimeField()
    to_utc_hour = models.TimeField()


class DayAndTimeSlot(models.Model):
    day_of_week = models.ForeignKey(DayOfWeek, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
