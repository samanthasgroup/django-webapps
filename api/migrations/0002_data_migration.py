import datetime

import yaml
from django.conf import settings
from django.db import migrations

from api.models.age_range import AgeRangeType
from api.models.choices.non_teaching_help_type import NonTeachingHelpType
from api.models.auxil.constants import (
    STUDENT_AGE_RANGES,
    STUDENT_AGE_RANGES_FOR_MATCHING,
    STUDENT_AGE_RANGES_FOR_TEACHER, LanguageLevelId,
    TIME_SLOTS
)
from api.models.auxil.data_populator import DataPopulator

APP_NAME = "api"


class InitialDataPopulator(DataPopulator):
    def _populate(self):
        """Populates the database with initial data."""
        self._write_age_ranges()
        self._write_day_and_time_slots()
        self._write_languages_and_levels()
        self._write_enrollment_tests()
        self._write_non_teaching_help()

    def _write_age_ranges(self):
        """Writes `AgeRange` objects to database."""
        AgeRange = self.apps.get_model(APP_NAME, "AgeRange")

        student_age_ranges = [
            AgeRange(type=AgeRangeType.STUDENT, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGES.values()  # keys are string ranges, not needed
        ]

        student_age_ranges_for_teacher = [
            AgeRange(type=AgeRangeType.TEACHER, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGES_FOR_TEACHER.values()
        ]

        student_age_ranges_for_matching = [
            AgeRange(type=AgeRangeType.MATCHING, age_from=pair[0], age_to=pair[1])
            for pair in STUDENT_AGE_RANGES_FOR_MATCHING.values()
        ]

        AgeRange.objects.bulk_create(
            student_age_ranges + student_age_ranges_for_teacher + student_age_ranges_for_matching
        )

    def _write_day_and_time_slots(self):
        """Writes `TimeSlot` and `DayAndTimeSlot` objects to database."""
        TimeSlot = self.apps.get_model(APP_NAME, "TimeSlot")
        DayAndTimeSlot = self.apps.get_model(APP_NAME, "DayAndTimeSlot")

        slots = (
            TimeSlot(
                from_utc_hour=datetime.time(hour=hour_from), to_utc_hour=datetime.time(hour=hour_to)
            )
            for hour_from, hour_to in TIME_SLOTS
        )
        TimeSlot.objects.bulk_create(slots)

        day_time_slots = (
            DayAndTimeSlot(day_of_week_index=day_idx, time_slot=time_slot)
            for day_idx in range(7)
            for time_slot in TimeSlot.objects.all()
        )
        DayAndTimeSlot.objects.bulk_create(day_time_slots)

    def _write_languages_and_levels(self):
        """Writes `Language`, `LanguageLevel`, and `LanguageAndLevel` objects to database."""
        Language = self.apps.get_model(APP_NAME, "Language")
        Level = self.apps.get_model(APP_NAME, "LanguageLevel")
        LanguageAndLevel = self.apps.get_model(APP_NAME, "LanguageAndLevel")

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
                ("fi", "Finnish"),
                ("gr", "Greek"),
                ("jp", "Japanese"),
            )
        )
        Language.objects.bulk_create(languages)

        levels = (Level(id=id_) for id_ in LanguageLevelId)
        Level.objects.bulk_create(levels)

        # English is taught at all levels, all other languages at levels A0 through A2
        language_and_level_objects = tuple(
            LanguageAndLevel(language=Language.objects.get(id="en"), level=level)
            for level in Level.objects.iterator()
        ) + tuple(
            LanguageAndLevel(language=language, level=level)
            for language in Language.objects.exclude(id="en").iterator()
            for level in Level.objects.filter(id__startswith="A").iterator()
        )
        LanguageAndLevel.objects.bulk_create(language_and_level_objects)

    def _write_enrollment_tests(self):
        """Writes `EnrollmentTest`, `Question`, and `EnrollmentTestQuestionOption` to database."""
        EnrollmentTest = self.apps.get_model(APP_NAME, "EnrollmentTest")
        EnrollmentTestQuestion = self.apps.get_model(APP_NAME, "EnrollmentTestQuestion")
        EnrollmentTestQuestionOption = self.apps.get_model(
            APP_NAME, "EnrollmentTestQuestionOption"
        )

        AgeRange = self.apps.get_model(APP_NAME, "AgeRange")

        path = (
            settings.BASE_DIR
            / APP_NAME
            / "migrations"
            / "data_migration_sources"
            / "enrollment_tests.yaml"
        )
        with path.open(encoding="utf8") as fh:
            data = yaml.safe_load(fh)

        # tests need to be saved to DB before adding questions to them,
        # as do questions before adding options, but options can be bulk_create()'d at the end
        question_options = []

        for block in data:
            # id for Language is a string, so no need to get object from database to get its id
            enrollment_test = EnrollmentTest.objects.create(language_id=block["language"])

            enrollment_test.age_ranges.set(
                AgeRange.objects.filter(
                    type=AgeRangeType.STUDENT,
                    age_from__gte=block["age_from"],
                    age_to__lte=block["age_to"],
                )
            )

            questions = block["questions"]

            for item in questions:
                question = EnrollmentTestQuestion.objects.create(
                    enrollment_test=enrollment_test, text=item["text"]
                )

                # make sure exactly one option is marked as correct in each question
                assert (
                    len([o for o in item["options"] if o["is_correct"] is True]) == 1
                ), f"Exactly 1 option has to be marked as correct for {item=}"

                question_options += [
                    EnrollmentTestQuestionOption(
                        question=question,
                        text=option_data["text"],
                        is_correct=option_data["is_correct"],
                    )
                    for option_data in item["options"]
                ] + [  # add "don't know" to each question
                    EnrollmentTestQuestionOption(
                        question=question,
                        text="(I don't know 😕)",
                        is_correct=False,
                    )
                ]

        EnrollmentTestQuestionOption.objects.bulk_create(question_options)

    def _write_non_teaching_help(self):
        NonTeachingHelp = self.apps.get_model(APP_NAME, "NonTeachingHelp")

        help_types = []
        for id_, name in NonTeachingHelpType.choices:
            help_types.append(NonTeachingHelp(id=id_, name=name))

        NonTeachingHelp.objects.bulk_create(help_types)


class Migration(migrations.Migration):
    dependencies = [
        (APP_NAME, "0001_initial"),
    ]

    operations = [
        migrations.RunPython(InitialDataPopulator.run, reverse_code=migrations.RunPython.noop)
    ]
