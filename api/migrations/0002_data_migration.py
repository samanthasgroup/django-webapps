import datetime

import yaml
from django.conf import settings
from django.db import migrations

from api.models.age_ranges import AgeRangeType
from api.models.constants import (
    STUDENT_AGE_RANGES,
    STUDENT_AGE_RANGES_FOR_MATCHING,
    STUDENT_AGE_RANGES_FOR_TEACHER,
)
from api.models.data_populator import DataPopulator

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
                from_utc_hour=datetime.time(hour=pair[0]), to_utc_hour=datetime.time(hour=pair[1])
            )
            for pair in ((5, 8), (8, 11), (11, 14), (14, 17), (17, 21))
        )
        TimeSlot.objects.bulk_create(slots)

        day_time_slots = (
            DayAndTimeSlot(day_of_week_index=day_idx, time_slot=time_slot)
            for day_idx in range(7)
            for time_slot in TimeSlot.objects.all()
        )
        DayAndTimeSlot.objects.bulk_create(day_time_slots)

    def _write_languages_and_levels(self):
        """Writes `Language', `LanguageLevel`, and `LanguageAndLevel` objects to database."""
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
            )
        )
        Language.objects.bulk_create(languages)

        # no C2 at this school
        levels = (Level(id=id_) for id_ in ("A0", "A1", "A2", "B1", "B2", "C1"))
        Level.objects.bulk_create(levels)

        language_and_level_objects = (
            LanguageAndLevel(language=language, level=level)
            for language in Language.objects.iterator()
            for level in Level.objects.iterator()
        )
        LanguageAndLevel.objects.bulk_create(language_and_level_objects)

    def _write_enrollment_tests(self):
        """Writes `EnrollmentTest', `Question`, and `EnrollmentTestQuestionOption` to database."""
        EnrollmentTest = self.apps.get_model(APP_NAME, "EnrollmentTest")
        EnrollmentTestQuestion = self.apps.get_model(APP_NAME, "EnrollmentTestQuestion")
        EnrollmentTestQuestionOption = self.apps.get_model(
            APP_NAME, "EnrollmentTestQuestionOption"
        )

        AgeRange = self.apps.get_model(APP_NAME, "AgeRange")
        Language = self.apps.get_model(APP_NAME, "Language")

        path = (
            settings.BASE_DIR
            / APP_NAME
            / "migrations"
            / "data_migration_sources"
            / "enrollment_test_en.yaml"
        )
        with path.open(encoding="utf8") as fh:
            data = yaml.safe_load(fh)

        for block in data:
            enrollment_test = EnrollmentTest(
                language=Language.objects.get(id=block["language"]),
            )

            enrollment_test.save()  # before adding m2m relationships
            enrollment_test.age_ranges.set(
                AgeRange.objects.filter(
                    type=AgeRangeType.STUDENT,
                    age_from__gte=block["age_from"],
                    age_to__lte=block["age_to"],
                )
            )

            questions = block["questions"]
            assert len(questions) == 35

            for item in questions:
                question = EnrollmentTestQuestion(
                    enrollment_test=enrollment_test, text=item["text"]
                )
                question.save()

                # make sure exactly one option is marked as correct in each question
                assert (
                    len([o for o in item["options"] if o["is_correct"] is True]) == 1
                ), f"Exactly 1 option has to be marked as correct for {item=}"

                for option_data in item["options"]:
                    EnrollmentTestQuestionOption.objects.create(
                        question=question,
                        text=option_data["text"],
                        is_correct=option_data["is_correct"],
                    )

                # add "don't know" to each question
                EnrollmentTestQuestionOption.objects.create(
                    question=question,
                    text="(I don't know 😕)",
                    is_correct=False,
                )

            enrollment_test.save()

    def _write_non_teaching_help(self):
        HelpType = self.apps.get_model(APP_NAME, "NonTeachingHelp")

        help_types = []
        for id_, name in (
            ("cv_write_edit", "CV and cover letter (write or edit)"),
            ("cv_proofread", "CV and cover letter (proofread)"),
            ("mock_interview", "Mock interview"),
            ("job_search", "Job search"),
            ("career_strategy", "Career strategy"),
            ("linkedin", "LinkedIn profile"),
            ("career_switch", "Career switch"),
            ("portfolio", "Portfolio for creative industries"),
            ("uni_abroad", "Entering a university abroad"),
            ("translate_docs", "Translation of documents"),
        ):
            help_types.append(HelpType(id=id_, name=name))

        HelpType.objects.bulk_create(help_types)


class Migration(migrations.Migration):
    dependencies = [
        (APP_NAME, "0001_initial"),
    ]

    operations = [
        migrations.RunPython(InitialDataPopulator.run, reverse_code=migrations.RunPython.noop)
    ]
