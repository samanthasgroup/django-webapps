import argparse
import csv
import datetime
import logging
import os
from collections.abc import Callable
from typing import TypeVar

import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()
from django.db import IntegrityError, transaction  # noqa: E402
from django.db.transaction import TransactionManagementError  # noqa: E402
from django.utils import timezone  # noqa: E402
from django_stubs_ext import QuerySetAny  # noqa: E402

from api.models.age_range import AgeRange  # noqa: E402
from api.models.choices.status.project import TeacherProjectStatus  # noqa: E402
from api.models.choices.status.situational import TeacherSituationalStatus  # noqa: E402
from api.models.day_and_time_slot import DayAndTimeSlot  # noqa: E402
from api.models.language_and_level import LanguageAndLevel  # noqa: E402
from api.models.personal_info import PersonalInfo  # noqa: E402
from api.models.teacher import Teacher  # noqa: E402
from django_webapps.scripts.db_population.parsers import (  # noqa: E402
    common_parsers,
    teacher_parsers,
)

RawTeacherType = list[list[str]]
ParseColumnReturnType = TypeVar("ParseColumnReturnType")
MAX_TID_WITH_NO_RESPONSE = 1300

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("teachers.log")
file_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(file_handler)

COLUMN_TO_ID = {
    "tid": 0,
    "cid": 1,
    "status": 3,
    "name": 4,
    "email": 5,
    "tg": 6,
    "timezone": 7,
    "experience": 8,
    "groups_number": 12,
    "age_ranges": 13,
    "language_levels": 14,
    "mon": 15,
    "tue": 16,
    "wed": 17,
    "thu": 18,
    "fri": 19,
    "sat": 20,
    "sun": 21,
    "speaking_club": 22,
    "can_give_feedback": 23,
    "other_help_comment": 24,
}


def warning_message(column_name: str, value: str) -> str:
    return f"{column_name} is not provided or can not be parsed, value: {value}"


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", "-i", required=True, help="Input csv file with teachers")
    return parser.parse_args()


def load_teachers(path_to_csv_file: str) -> list[list[str]]:
    with open(path_to_csv_file, newline="") as csvfile:  # noqa: PTH123
        return list(csv.reader(csvfile))


class TeacherPopulator:
    def __init__(self, teachers: RawTeacherType) -> None:
        self.teachers = self._pre_process_teachers(teachers[1:])
        self.header = teachers[0]
        self._current_teacher = None

    def run(self) -> None:
        for teacher in tqdm(self.teachers, desc="Processing teachers..."):
            tid = teacher[COLUMN_TO_ID["tid"]]
            logger.info("======================================================= ")
            logger.info(f"Parsing teacher with tid {tid}")
            self._current_teacher = teacher
            self._create_teacher()

    def _pre_process_teachers(self, teachers: RawTeacherType) -> RawTeacherType:
        teachers.sort(key=lambda teacher: int(teacher[COLUMN_TO_ID["tid"]]))
        return teachers

    @transaction.atomic
    def _create_teacher(self) -> None:
        if self._current_teacher is None:
            raise TypeError("Value of current teacher can not be None")

        status = self._parse_cell("status", teacher_parsers.parse_status)
        tid = int(self._current_teacher[COLUMN_TO_ID["tid"]])
        if status is None or (
            status[0] == TeacherSituationalStatus.NO_RESPONSE and tid > MAX_TID_WITH_NO_RESPONSE
        ):
            logger.info(
                "Skipping teacher since there was no response from them or status is unclear"
            )
            return

        none_teaching_help_comment = self._current_teacher[COLUMN_TO_ID["other_help_comment"]]
        has_experience = self._parse_cell("experience", teacher_parsers.parse_has_experience)
        can_give_feedback = self._parse_cell(
            "can_give_feedback", teacher_parsers.parse_can_give_feedback
        )
        groups_number = self._parse_cell("groups_number", teacher_parsers.parse_groups_number)
        speaking_club = self._parse_cell("speaking_club", teacher_parsers.parse_speaking_club)
        project_status = status[0] if type(status[0]) == TeacherProjectStatus else None
        situational_status = status[0] if type(status[0]) == TeacherSituationalStatus else None
        try:
            personal_info = self._create_personal_info()
            availability_slots = self._create_availability_slots()
            languages_and_levels = self._create_language_and_levels()
            age_ranges = self._create_age_ranges()
            teacher = Teacher.objects.create(
                project_status=project_status,
                has_prior_teaching_experience=has_experience or False,
                peer_support_can_give_feedback=can_give_feedback or False,
                simultaneous_groups=groups_number or 1,
                can_host_speaking_club=speaking_club or False,
                personal_info=personal_info,
                status_since=timezone.now(),
                is_validated=project_status == TeacherProjectStatus.WORKING,
                weekly_frequency_per_group=2,
                non_teaching_help_provided_comment=none_teaching_help_comment,
                has_hosted_speaking_club=status[1]
                == teacher_parsers.ProjectStatusAction.SPEAKING_CLUB,
            )
            if situational_status is not None:
                teacher.situational_status = situational_status
            teacher.student_age_ranges.set(age_ranges)
            teacher.availability_slots.set(availability_slots)
            teacher.teaching_languages_and_levels.set(languages_and_levels)
            teacher.save()
            logger.info(f"Successfully Parsed Teacher with tid {tid}")
        except (IntegrityError, TransactionManagementError) as e:
            logger.info(f"Teacher with tid {tid} can not be parsed, see errors above")
            logger.debug(e)

    def _report_error(self, error: ValueError) -> None:
        logger.error(error)

    def _parse_cell(
        self,
        column_name: str,
        parser: Callable[..., ParseColumnReturnType],
        skip_if_empty: bool = False,
    ) -> ParseColumnReturnType | None:
        if self._current_teacher is None:
            raise TypeError("Value of current teacher can not be None")
        index = COLUMN_TO_ID[column_name]
        if skip_if_empty and self._current_teacher[index].strip() == "":
            return None
        try:
            result = parser(self._current_teacher[index])
            if result is None or (isinstance(result, list) and len(result) == 0):
                logger.warning(warning_message(self.header[index], self._current_teacher[index]))
            return result
        except ValueError as error:
            self._report_error(error)
        return None

    def _create_age_ranges(self) -> QuerySetAny[AgeRange, AgeRange]:
        age_ranges = self._parse_cell("age_ranges", teacher_parsers.parse_age_ranges)
        if age_ranges:
            return AgeRange.objects.all()
        return AgeRange.objects.filter(age_from=17)

    def _create_personal_info(self) -> None | PersonalInfo:
        name = self._parse_cell("name", teacher_parsers.parse_name)
        telegram_username = self._parse_cell("tg", common_parsers.parse_telegram_name)
        timezone = self._parse_cell("timezone", common_parsers.parse_timezone)
        email = self._parse_cell("email", common_parsers.parse_email)
        if name is None or telegram_username is None or email is None:
            return None

        utc_timedelta = None
        if timezone is not None:
            utc_timedelta = timezone.utcoffset(None) or datetime.timedelta(hours=0)
        try:
            return PersonalInfo.objects.create(
                first_name=name,
                last_name="",
                telegram_username=telegram_username,
                email=email,
                utc_timedelta=utc_timedelta or datetime.timedelta(hours=0),
            )
        except IntegrityError as _:
            logger.warning("Teacher might be a duplicate")
        return None

    def _create_language_and_levels(self) -> QuerySetAny[LanguageAndLevel, LanguageAndLevel]:
        levels = self._parse_cell("language_levels", teacher_parsers.parse_language_level)
        if levels is None:
            return LanguageAndLevel.objects.filter(language__name="english")
        return LanguageAndLevel.objects.filter(language__name="english", level__id__in=levels)

    def _create_availability_slots(self) -> list[DayAndTimeSlot]:
        result: list[DayAndTimeSlot] = []
        for day_index, day in enumerate(["mon", "tue", "wed", "thu", "fri", "sat", "sun"]):
            slots = (
                self._parse_cell(day, teacher_parsers.parse_availability_slots, skip_if_empty=True)
                or []
            )
            for slot in slots:
                result.extend(
                    DayAndTimeSlot.objects.filter(
                        day_of_week_index=day_index,
                        time_slot__from_utc_hour=datetime.time(hour=slot[0]),
                        time_slot__to_utc_hour=datetime.time(hour=slot[1]),
                    )
                )
        return result

    def _create_comment(self) -> str:
        if self._current_teacher is None:
            raise TypeError("Value of current teacher can not be None")
        rows = ["======= OLD CSV DATA =======\n"]
        for index in COLUMN_TO_ID.values():
            rows.append(f"{self.header[index]} - {self._current_teacher[index]}")
        return "\n".join(rows)


if __name__ == "__main__":
    args = get_args()
    teachers = load_teachers(args.input_csv)
    populator = TeacherPopulator(teachers)
    populator.run()
