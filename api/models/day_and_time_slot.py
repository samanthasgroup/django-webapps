from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeSlot(models.Model):
    """Model for timeslots. Note that the timeslots have no "name" as such.

    Will be pre-populated.
    """

    # Postgres supports ranges, and in Django we could use IntegerRangeField for a Postgres range,
    # but that would hinder development and testing with SQLite.
    # Also, Postgres has no pure time ranges (only date-time).
    from_utc_hour = models.TimeField(verbose_name=_("from UTC hour"))
    to_utc_hour = models.TimeField(verbose_name=_("to UTC hour"))

    class Meta:
        constraints = [models.UniqueConstraint(fields=["from_utc_hour", "to_utc_hour"], name="from_to_hour")]

    verbose_name = _("time slot")
    verbose_name_plural = _("time slots")

    def __str__(self) -> str:
        return f"{self.from_utc_hour.strftime('%H:%M')}-{self.to_utc_hour.strftime('%H:%M')} UTC"


class DayAndTimeSlot(models.Model):
    """Model for combinations of days and timeslots. Will be pre-populated."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, _("Monday")
        TUESDAY = 1, _("Tuesday")
        WEDNESDAY = 2, _("Wednesday")
        THURSDAY = 3, _("Thursday")
        FRIDAY = 4, _("Friday")
        SATURDAY = 5, _("Saturday")
        SUNDAY = 6, _("Sunday")

    day_of_week_index = models.PositiveSmallIntegerField(choices=DayOfWeek.choices, verbose_name=_("day of the week"))
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name=_("time slot"))

    class Meta:
        verbose_name = _("day and time slot")
        verbose_name_plural = _("days and time slots")
        constraints = [models.UniqueConstraint(fields=["day_of_week_index", "time_slot"], name="unique_day_and_slot")]
        ordering = ("day_of_week_index", "time_slot__from_utc_hour")

    def __str__(self) -> str:
        return f"{self.get_day_of_week_index_display()}, {self.time_slot}"
