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
        """Runs pre-population operations."""
        self._write_age_ranges()
        self._write_time_slots()
        self._write_day_and_time_slot_objects()
        self._write_levels()
        self._write_languages()
        self._write_language_and_level_objects()

    def _write_age_ranges(self):
        """Writes `AgeRange` objects to database."""
        AgeRange = self.apps.get_model("api", "AgeRange")

        student_age_ranges = [
            AgeRange(type=AgeRangeType.STUDENT, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGE_BOUNDARIES.values()  # keys are string ranges, not needed
        ]

        student_age_ranges_for_teacher = [
            AgeRange(type=AgeRangeType.TEACHER, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGE_BOUNDARIES_FOR_TEACHER.values()
        ]

        # TODO ranges for matching

        AgeRange.objects.bulk_create(student_age_ranges + student_age_ranges_for_teacher)

    def _write_time_slots(self):
        """Writes `TimeSlot` objects to database."""
        TimeSlot = self.apps.get_model("api", "TimeSlot")

        slots = (
            TimeSlot(
                from_utc_hour=datetime.time(hour=pair[0]), to_utc_hour=datetime.time(hour=pair[1])
            )
            for pair in ((5, 8), (8, 11), (11, 14), (14, 17), (17, 21))
        )
        TimeSlot.objects.bulk_create(slots)

    def _write_day_and_time_slot_objects(self):
        """Writes `DayAndTimeSlot` objects to database."""
        TimeSlot = self.apps.get_model("api", "TimeSlot")
        DayAndTimeSlot = self.apps.get_model("api", "DayAndTimeSlot")

        day_time_slots = (
            DayAndTimeSlot(day_of_week_index=day_idx, time_slot=time_slot)
            for day_idx in range(7)
            for time_slot in TimeSlot.objects.all()
        )
        DayAndTimeSlot.objects.bulk_create(day_time_slots)

    def _write_levels(self):
        """Writes `LanguageLevel` objects to database."""
        Level = self.apps.get_model("api", "LanguageLevel")
        # no C2 at this school
        levels = (Level(id=id_) for id_ in ("A0", "A1", "A2", "B1", "B2", "C1"))
        Level.objects.bulk_create(levels)

    def _write_languages(self):
        """Writes `Language` objects to database."""
        Language = self.apps.get_model("api", "Language")
        languages = (
            Language(id=pair[0], name=pair[1])
            for pair in (
                ("en", "English"),
                ("fr", "French"),
                ("de", "German"),
                ("es", "Spanish"),
                ("it", "Italian"),
                ("pl", "Polish"),
                ("cz", "Czech"),
                ("se", "Swedish"),
            )
        )
        Language.objects.bulk_create(languages)

    def _write_language_and_level_objects(self):
        """Writes `LanguageAndLevel` objects to database."""
        Language = self.apps.get_model("api", "Language")
        Level = self.apps.get_model("api", "LanguageLevel")
        LanguageAndLevel = self.apps.get_model("api", "LanguageAndLevel")

        language_and_level_objects = (
            LanguageAndLevel(language=language, level=level)
            for language in Language.objects.iterator()
            for level in Level.objects.iterator()
        )
        LanguageAndLevel.objects.bulk_create(language_and_level_objects)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [migrations.RunPython(PrePopulationMaster)]
