import datetime
import os
from dataclasses import dataclass, field

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()

from django.db import IntegrityError, transaction  # noqa: E402
from django.db.transaction import TransactionManagementError  # noqa: E402
from django.utils import timezone  # noqa: E402

from api.models.age_range import AgeRange  # noqa: E402
from api.models.choices.status.project import StudentProjectStatus  # noqa: E402
from api.models.choices.status.situational import StudentSituationalStatus  # noqa: E402
from api.models.student import Student  # noqa: E402
from devtools.scripts.db_population.base_populator import (  # noqa: E402
    BasePersonEntityData,
    BasePopulatorFromCsv,
    CsvData,
)
from devtools.scripts.db_population.parsers import common_parsers, student_parsers  # noqa: E402
from devtools.scripts.db_population.utils import get_args, get_logger, load_csv_data  # noqa: E402

logger = get_logger("students.log")
MIN_SID_WITH_NO_RESPONSE = 1300


COLUMN_TO_ID = {
    "sid": 0,
    "cid": 1,
    "coord": 2,
    "tid": 3,
    "teacher": 4,
    "gid": 5,
    "status": 6,
    "email": 7,
    "name": 8,
    "age": 9,
    "language_level": 10,
    "desired_language_level": 11,
    "mon": 12,
    "tue": 13,
    "wed": 14,
    "thu": 15,
    "fri": 16,
    "sat": 17,
    "sun": 18,
    "timezone": 19,
    "phone": 20,
    "comment": 22,
    "coord_comment": 23,
}


@dataclass
class StudentData(BasePersonEntityData):
    age_range: tuple[int, int] | None = None
    project_status: StudentProjectStatus = StudentProjectStatus.STUDYING
    utc_timedelta: datetime.timedelta = datetime.timedelta(hours=0)
    last_name: str = ""
    status_since: datetime.datetime = timezone.now()
    availability_slots: list[list[tuple[int, int]]] = field(default_factory=list)
    languages_and_levels: list[str] = field(default_factory=list)
    situational_status: StudentSituationalStatus | None = None


class StudentPopulator(BasePopulatorFromCsv):
    id_name: str = "sid"
    entity_name: str = "student"

    def _pre_process_data(self, csv_data: CsvData) -> CsvData:
        return super()._pre_process_data(csv_data)

    def _get_entity_data(self) -> Student | None:
        if self._current_entity is None:
            raise TypeError("Value of current student can not be None")

        parsed_status = self._parse_cell("status", student_parsers.parse_status)
        sid = int(self._current_entity[self._column_to_id[self.id_name]])
        if parsed_status is None:
            logger.error(f"{sid}: skipping since status is unclear")
            return None
        if (
            parsed_status[0] == StudentSituationalStatus.NO_RESPONSE
            and sid < MIN_SID_WITH_NO_RESPONSE
        ):
            logger.info(
                f"{sid}: skipping since no response, and sid is below: {MIN_SID_WITH_NO_RESPONSE}"
            )
            return None

        name = self._parse_cell("name", common_parsers.parse_name)
        project_status = parsed_status[1]
        phone = self._parse_cell("phone", common_parsers.parse_phone_number)
        tg = (
            self._parse_cell("phone", common_parsers.parse_telegram_name)
            if phone is None
            else None
        )
        email = self._parse_cell("email", common_parsers.parse_email)
        student_data = StudentData(
            email=email,
            first_name=name,
            project_status=project_status,
            phone_number=phone,
            id=sid,
            telegram_username=tg,
        )
        timezone = self._parse_cell("timezone", common_parsers.parse_timezone, skip_if_empty=True)
        student_data.utc_timedelta = timezone.utcoffset(None) if timezone else None
        student_data.situational_status = parsed_status[1]
        student_data.age_range = self._parse_cell("age", student_parsers.parse_age_range)
        student_data.languages_and_levels = self._parse_cell(
            "language_level", common_parsers.parse_language_level, skip_if_empty=True
        )
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            slots = self._parse_cell(
                day, common_parsers.parse_availability_slots, skip_if_empty=True
            )
            if slots is not None:
                student_data.availability_slots.append(slots)
        return student_data

    @transaction.atomic
    def _create_entity(self, entity_data: StudentData) -> None:
        try:
            personal_info = self._create_personal_info(entity_data)
            age_range = self._create_age_range(entity_data.age_range)
            if personal_info is None or age_range is None:
                raise ValueError("Unable to create mandatory data")

            if Student.objects.filter(legacy_sid=entity_data.id).count():
                logger.warning(
                    f"Student with {self.id_name} {entity_data.id} was already migrated"
                )
                return

            student = Student.objects.create(
                legacy_sid=entity_data.id,
                age_range=age_range,
                project_status=entity_data.project_status,
                personal_info=personal_info,
                status_since=entity_data.status_since,
                comment=self._create_comment(),
            )
            if entity_data.situational_status is not None:
                student.situational_status = entity_data.situational_status
            student.availability_slots.set(
                self._create_availability_slots(entity_data.availability_slots)
            )
            student.teaching_languages_and_levels.set(
                self._create_language_and_levels(entity_data.languages_and_levels)
            )
            student.save()
            self._update_metadata(entity_data.id, student.personal_info.id, entity_data.first_name)
            logger.info(
                f"Student migrated, old id: {entity_data.id}, new id: {student.personal_info.id}"
            )
        except (IntegrityError, TransactionManagementError, ValueError) as e:
            logger.warning(
                f"Student with {self.id_name} {entity_data.id} can not be parsed, see errors above"
            )
            logger.debug(e)

    def _create_age_range(self, age_range: tuple[int, int] | None) -> AgeRange | None:
        if age_range is None:
            return None
        return AgeRange.objects.filter(age_from=age_range[0], age_to=age_range[1]).first()

    def _update_metadata(self, old_id: int, new_id: int, name: str) -> None:
        self._metadata[self.entity_name].append({"name": name, "old_id": old_id, "new_id": new_id})


if __name__ == "__main__":
    args = get_args()
    students = load_csv_data(args.input_csv)
    populator = StudentPopulator(students, COLUMN_TO_ID, dry=args.dry, logger=logger)
    populator.run()
