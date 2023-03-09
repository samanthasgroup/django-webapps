# Generated by Django 4.1.7 on 2023-03-05 16:47
import datetime

from django.db import migrations
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor  # for typing only
from django.db.migrations.state import StateApps  # for typing only

from api.models.constants import (
    STUDENT_AGE_RANGE_BOUNDARIES,
    # STUDENT_AGE_RANGE_BOUNDARIES_FOR_MATCHING,
    STUDENT_AGE_RANGE_BOUNDARIES_FOR_TEACHER,
)
from api.models.age_ranges import AgeRangeType


class PrePopulationMaster:
    """Class-based variation of functions for pre-populating the database with fixed data.
    See Django docs: https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations
    """

    def __init__(self, apps: StateApps, schema_editor: DatabaseSchemaEditor):
        self.apps = apps
        self.schema_editor = schema_editor
        # Adding __call__ to a class won't work because RunPython can't create an instance and then
        # run it.  So we're running main() right after instantiating, which effectively makes
        # PrePopulationMaster into a callable with instance attributes.
        self.main()

    def main(self):
        self._write_age_ranges()
        self._write_time_slots()
        self._write_day_and_time_slots()
        self._write_levels()

    def _write_age_ranges(self):
        AgeRange = self.apps.get_model("api", "AgeRange")

        student_age_ranges = [
            AgeRange(type=AgeRangeType.STUDENT, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGE_BOUNDARIES.values()  # keys are string ranges, we don't need them
        ]

        student_age_ranges_for_teacher = [
            AgeRange(type=AgeRangeType.TEACHER, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGE_BOUNDARIES_FOR_TEACHER.values()
        ]

        # TODO ranges for matching

        AgeRange.objects.bulk_create(student_age_ranges + student_age_ranges_for_teacher)

    def _write_time_slots(self):
        TimeSlot = self.apps.get_model("api", "TimeSlot")

        slots_dicts = (
            {"from_utc_hour": datetime.time(hour=from_), "to_utc_hour": datetime.time(hour=to)}
            for from_, to in ((5, 8), (8, 11), (11, 14), (14, 17), (17, 21))
        )
        slots = (TimeSlot(**dict_) for dict_ in slots_dicts)
        TimeSlot.objects.bulk_create(slots)

    def _write_day_and_time_slots(self):
        TimeSlot = self.apps.get_model("api", "TimeSlot")
        DayAndTimeSlot = self.apps.get_model("api", "DayAndTimeSlot")

        day_time_slots = (
            DayAndTimeSlot(day_of_week_index=day_idx, time_slot=time_slot)
            for day_idx in range(7)
            for time_slot in TimeSlot.objects.all()
        )
        DayAndTimeSlot.objects.bulk_create(day_time_slots)

    def _write_levels(self):
        Level = self.apps.get_model("api", "LanguageLevel")
        # no C2 at this school
        levels = (Level(id=id_) for id_ in ("A0", "A1", "A2", "B1", "B2", "C1"))
        Level.objects.bulk_create(levels)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [migrations.RunPython(PrePopulationMaster)]
