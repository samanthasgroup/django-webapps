from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeSlot(models.Model):
    """Model for timeslots. Note that the timeslots have no "name" as such.

    Will be pre-populated.
    """

    # Postgres supports ranges, and in Django we could use IntegerRangeField for a Postgres range,
    # but that would hinder development and testing with SQLite.
    # Also, Postgres has no pure time ranges (only date-time).
    from_utc_hour = models.TimeField()
    to_utc_hour = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_utc_hour", "to_utc_hour"], name="from_to_hour")
        ]

    def __str__(self) -> str:
        return f"{self.from_utc_hour.strftime('%H:%M')}-{self.to_utc_hour.strftime('%H:%M')} UTC"


class DayAndTimeSlot(models.Model):
    """Model for combinations of days and timeslots. Will be pre-populated."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    day_of_week_index = models.PositiveSmallIntegerField(
        choices=DayOfWeek.choices, verbose_name=_("day of the week")
    )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["day_of_week_index", "time_slot"], name="unique_day_and_slot"
            )
        ]
        ordering = ("day_of_week_index", "time_slot__from_utc_hour")

    def __str__(self) -> str:
        return f"{self.get_day_of_week_index_display()}, {self.time_slot}"
