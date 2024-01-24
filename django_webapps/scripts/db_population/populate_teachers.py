import argparse
import csv
import datetime
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

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
    parser.add_argument(
        "--input_csv", "-i", type=str, required=True, help="Input csv file with teachers"
    )
    parser.add_argument(
        "--dry",
        "-d",
        type=bool,
        help="dry mode, prevent from inserting data into the database",
        default=False,
    )
    return parser.parse_args()


def load_teachers(path_to_csv_file: str) -> list[list[str]]:
    with open(path_to_csv_file, newline="") as csvfile:  # noqa: PTH123
        return list(csv.reader(csvfile))


@dataclass
class TeacherData:
    email: str
    first_name: str
    telegram_username: str
    project_status: TeacherProjectStatus
    tid: int
    utc_timedelta: datetime.timedelta = datetime.timedelta(hours=0)
    has_prior_teaching_experience: bool = False
    peer_support_can_give_feedback: bool = False
    has_hosted_speaking_club: bool = False
    can_host_speaking_club: bool = False
    weekly_frequency_per_group: int = 2
    status_since: datetime.datetime = timezone.now()
    is_validated: bool = False
    simultaneous_groups: int = 1
    non_teaching_help_provided_comment: str = ""
    last_name: str = ""
    student_age_ranges: bool = False
    availability_slots: list[list[tuple[int, int]]] = field(default_factory=list)
    teaching_languages_and_levels: list[str] = field(default_factory=list)
    situational_status: TeacherSituationalStatus | None = None

    # use default values
    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, name, None) is not None and value is None:
            return
        super().__setattr__(name, value)


class TeacherPopulator:
    def __init__(self, teachers: RawTeacherType, dry: bool = False) -> None:
        self.teachers = self._pre_process_teachers(teachers[1:])
        self.header = teachers[0]
        self.header[0] = "tid"
        self._dry = dry
        self._current_teacher = None

    def run(self) -> None:
        for teacher in tqdm(self.teachers, desc="Processing teachers..."):
            tid = teacher[COLUMN_TO_ID["tid"]]
            logger.info("======================================================= ")
            logger.info(f"Parsing teacher with tid {tid}")
            self._current_teacher = teacher

            teacher_data = self._get_teacher_data()
            if teacher_data is None:
                continue

            if not self._dry:
                self._create_teacher(teacher_data)

    def _pre_process_teachers(self, teachers: RawTeacherType) -> RawTeacherType:
        teachers.sort(key=lambda teacher: int(teacher[COLUMN_TO_ID["tid"]]))
        return teachers

    def _get_teacher_data(self) -> TeacherData | None:
        if self._current_teacher is None:
            raise TypeError("Value of current teacher can not be None")

        parsed_status = self._parse_cell("status", teacher_parsers.parse_status)
        tid = int(self._current_teacher[COLUMN_TO_ID["tid"]])
        if parsed_status is None or (
            parsed_status[1] == TeacherSituationalStatus.NO_RESPONSE
            and tid > MAX_TID_WITH_NO_RESPONSE
        ):
            logger.info(
                "Skipping teacher since there was no response from them or status is unclear"
            )
            return None

        name = self._parse_cell("name", teacher_parsers.parse_name)
        project_status = parsed_status[1]
        telegram_username = self._parse_cell("tg", common_parsers.parse_telegram_name)
        email = self._parse_cell("email", common_parsers.parse_email)
        teacher_data = TeacherData(
            email=email,
            first_name=name,
            telegram_username=telegram_username,
            project_status=project_status,
            tid=tid,
        )
        timezone = self._parse_cell("timezone", common_parsers.parse_timezone)
        teacher_data.utc_timedelta = timezone.utcoffset(None) if timezone else None
        teacher_data.situational_status = parsed_status[1]
        teacher_data.student_age_ranges = self._parse_cell(
            "age_ranges", teacher_parsers.parse_age_ranges
        )
        teacher_data.none_teaching_help_comment = self._current_teacher[
            COLUMN_TO_ID["other_help_comment"]
        ]
        teacher_data.has_prior_teaching_experience = self._parse_cell(
            "experience", teacher_parsers.parse_has_experience
        )
        teacher_data.peer_support_can_give_feedback = self._parse_cell(
            "can_give_feedback", teacher_parsers.parse_can_give_feedback
        )
        teacher_data.simultaneous_groups = self._parse_cell(
            "groups_number", teacher_parsers.parse_groups_number
        )
        teacher_data.can_host_speaking_club = self._parse_cell(
            "speaking_club", teacher_parsers.parse_speaking_club
        )
        teacher_data.teaching_languages_and_levels = self._parse_cell(
            "language_levels", teacher_parsers.parse_language_level
        )
        teacher_data.is_validated = project_status == TeacherProjectStatus.WORKING
        teacher_data.has_hosted_speaking_club = (
            project_status == teacher_parsers.ProjectStatusAction.SPEAKING_CLUB
        )
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            slots = self._parse_cell(
                day, teacher_parsers.parse_availability_slots, skip_if_empty=True
            )
            if slots is not None:
                teacher_data.availability_slots.append(slots)
        return teacher_data

    @transaction.atomic
    def _create_teacher(self, teacher_data: TeacherData) -> None:
        try:
            personal_info = self._create_personal_info(teacher_data)
            if personal_info is None:
                return
            teacher = Teacher.objects.create(
                project_status=teacher_data.project_status,
                has_prior_teaching_experience=teacher_data.has_prior_teaching_experience,
                peer_support_can_give_feedback=teacher_data.peer_support_can_give_feedback,
                simultaneous_groups=teacher_data.simultaneous_groups,
                can_host_speaking_club=teacher_data.can_host_speaking_club,
                personal_info=personal_info,
                status_since=teacher_data.status_since,
                is_validated=teacher_data.is_validated,
                weekly_frequency_per_group=teacher_data.weekly_frequency_per_group,
                non_teaching_help_provided_comment=teacher_data.non_teaching_help_provided_comment,
                has_hosted_speaking_club=teacher_data.has_hosted_speaking_club,
                comment=self._create_comment(),
            )
            if teacher_data.situational_status is not None:
                teacher.situational_status = teacher_data.situational_status
            teacher.student_age_ranges.set(
                self._create_age_ranges(teacher_data.student_age_ranges)
            )
            teacher.availability_slots.set(
                self._create_availability_slots(teacher_data.availability_slots)
            )
            teacher.teaching_languages_and_levels.set(
                self._create_language_and_levels(teacher_data.teaching_languages_and_levels)
            )
            teacher.save()
            logger.info(f"Successfully created Teacher with tid {teacher_data.tid}")
        except (IntegrityError, TransactionManagementError) as e:
            logger.warning(
                f"Teacher with tid {teacher_data.tid} can not be parsed, see errors above"
            )
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

    def _create_age_ranges(self, age_ranges: bool) -> QuerySetAny[AgeRange, AgeRange]:
        if age_ranges:
            return AgeRange.objects.all()
        return AgeRange.objects.filter(age_from=17)

    def _create_personal_info(self, teacher_data: TeacherData) -> None | PersonalInfo:
        if (
            teacher_data.first_name is None
            or teacher_data.telegram_username is None
            or teacher_data.email is None
        ):
            return None
        try:
            return PersonalInfo.objects.create(
                first_name=teacher_data.first_name,
                last_name=teacher_data.last_name,
                telegram_username=teacher_data.telegram_username,
                email=teacher_data.email,
                utc_timedelta=teacher_data.utc_timedelta,
            )
        except IntegrityError as _:
            logger.warning("Teacher might be a duplicate")
        return None

    def _create_language_and_levels(
        self, levels: list[str]
    ) -> QuerySetAny[LanguageAndLevel, LanguageAndLevel]:
        if len(levels) == 0:
            return LanguageAndLevel.objects.filter(language__name="English")
        return LanguageAndLevel.objects.filter(language__name="English", level__id__in=levels)

    def _create_availability_slots(
        self, weekly_slots: list[list[tuple[int, int]]]
    ) -> list[DayAndTimeSlot]:
        result: list[DayAndTimeSlot] = []
        for day_index, slots in enumerate(weekly_slots):
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
        rows = ["======= OLD CSV DATA ======="]
        for index in COLUMN_TO_ID.values():
            rows.append(f"{self.header[index]} - {self._current_teacher[index]}\n")
        rows.append("======= OLD CSV DATA =======")
        return "\n".join(rows)


if __name__ == "__main__":
    args = get_args()
    teachers = load_teachers(args.input_csv)
    populator = TeacherPopulator(teachers, args.dry)
    populator.run()
