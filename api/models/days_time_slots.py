from django.db import models

from api.models.auxil import MultilingualModel


class DayOfWeek(MultilingualModel):
    """Model for days of the week (with internationalization)."""

    # We could just use numbers and then localize them using Babel,
    # but it seems easier to just create a table with 7 rows.
    index = models.PositiveSmallIntegerField()  # it's best not to rely on automatic ID here

    class Meta:
        ordering = ("index",)
        verbose_name_plural = "days of the week"


class TimeSlot(models.Model):
    # Postgres supports ranges, and in Django we could use IntegerRangeField for a Postgres range,
    # but that would hinder development and testing with SQLite.
    # Also, Postgres has no pure time ranges (only date-time).
    from_utc_hour = models.TimeField()
    to_utc_hour = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_utc_hour", "to_utc_hour"], name="from_to_hour")
        ]

    def __str__(self):
        return f"{self.from_utc_hour.strftime('%H:%M')}-{self.to_utc_hour.strftime('%H:%M')} UTC"


class DayAndTimeSlot(models.Model):
    day_of_week = models.ForeignKey(DayOfWeek, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["day_of_week", "time_slot"], name="day_and_slot")
        ]
        ordering = ("day_of_week__index", "time_slot__from_utc_hour")

    def __str__(self):
        return f"{self.day_of_week}, {self.time_slot}"
