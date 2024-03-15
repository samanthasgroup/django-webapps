import datetime
import os
from dataclasses import dataclass, field

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()

from django.db import IntegrityError, transaction  # noqa: E402
from django.db.transaction import TransactionManagementError  # noqa: E402
from django.utils import timezone  # noqa: E402
from django_stubs_ext import QuerySetAny  # noqa: E402

from api.models.age_range import AgeRange  # noqa: E402
from api.models.choices.status.project import TeacherProjectStatus  # noqa: E402
from api.models.choices.status.situational import TeacherSituationalStatus  # noqa: E402
from api.models.teacher import Teacher  # noqa: E402
from django_webapps.scripts.db_population.base_populator import (  # noqa: E402
    BasePersonEntityData,
    BasePopulatorFromCsv,
    CsvData,
)
from django_webapps.scripts.db_population.parsers import (  # noqa: E402
    common_parsers,
    teacher_parsers,
)
from django_webapps.scripts.db_population.utils import (  # noqa: E402
    get_args,
    get_logger,
    load_csv_data,
)

logger = get_logger("teachers.log")
MIN_TID_WITH_NO_RESPONSE = 1300


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


@dataclass
class TeacherData(BasePersonEntityData):
    project_status: TeacherProjectStatus = TeacherProjectStatus.WORKING
    utc_timedelta: datetime.timedelta = datetime.timedelta(hours=0)
    last_name: str = ""
    has_prior_teaching_experience: bool = False
    peer_support_can_give_feedback: bool = False
    has_hosted_speaking_club: bool = False
    can_host_speaking_club: bool = False
    weekly_frequency_per_group: int = 2
    status_since: datetime.datetime = timezone.now()
    is_validated: bool = False
    simultaneous_groups: int = 1
    non_teaching_help_provided_comment: str = ""
    is_teaching_children: bool = False
    availability_slots: list[list[tuple[int, int]]] = field(default_factory=list)
    teaching_languages_and_levels: list[str] = field(default_factory=list)
    situational_status: TeacherSituationalStatus | None = None


class TeacherPopulator(BasePopulatorFromCsv):
    id_name: str = "tid"
    entity_name: str = "teacher"

    def _pre_process_data(self, csv_data: CsvData) -> CsvData:
        return super()._pre_process_data(csv_data)

    def _get_entity_data(self) -> TeacherData | None:
        if self._current_entity is None:
            raise TypeError("Value of current teacher can not be None")

        parsed_status = self._parse_cell("status", teacher_parsers.parse_status)
        tid = int(self._current_entity[self._column_to_id[self.id_name]])

        if parsed_status is None:
            logger.info(f"{tid}: skipping teacher since status is unclear")
            return None
        if (
            parsed_status[0] == TeacherSituationalStatus.NO_RESPONSE
            and tid < MIN_TID_WITH_NO_RESPONSE
        ):
            logger.info(
                f"{tid}: skipping since no response, and sid is below: {MIN_TID_WITH_NO_RESPONSE}"
            )
            return None

        name = self._parse_cell("name", common_parsers.parse_name)
        project_status = parsed_status[1]
        telegram_username = self._parse_cell("tg", common_parsers.parse_telegram_name)
        phone = (
            self._parse_cell("tg", common_parsers.parse_phone_number)
            if telegram_username is None
            else None
        )
        email = self._parse_cell("email", common_parsers.parse_email)
        teacher_data = TeacherData(
            email=email,
            first_name=name,
            telegram_username=telegram_username,
            project_status=project_status,
            phone_number=phone,
            id=tid,
        )
        timezone = self._parse_cell("timezone", common_parsers.parse_timezone, skip_if_empty=True)
        teacher_data.utc_timedelta = timezone.utcoffset(None) if timezone else None
        teacher_data.situational_status = parsed_status[1]
        teacher_data.is_teaching_children = self._parse_cell(
            "age_ranges", teacher_parsers.parse_age_ranges, skip_if_empty=True
        )
        teacher_data.none_teaching_help_comment = self._current_entity[
            COLUMN_TO_ID["other_help_comment"]
        ]
        teacher_data.has_prior_teaching_experience = self._parse_cell(
            "experience", teacher_parsers.parse_has_experience, skip_if_empty=True
        )
        teacher_data.peer_support_can_give_feedback = self._parse_cell(
            "can_give_feedback", teacher_parsers.parse_can_give_feedback, skip_if_empty=True
        )
        teacher_data.simultaneous_groups = self._parse_cell(
            "groups_number", teacher_parsers.parse_groups_number, skip_if_empty=True
        )
        teacher_data.can_host_speaking_club = self._parse_cell(
            "speaking_club", teacher_parsers.parse_speaking_club, skip_if_empty=True
        )
        teacher_data.teaching_languages_and_levels = self._parse_cell(
            "language_levels", common_parsers.parse_language_level, skip_if_empty=True
        )
        teacher_data.has_hosted_speaking_club = (
            project_status == teacher_parsers.ProjectStatusAction.SPEAKING_CLUB
        )
        for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            slots = self._parse_cell(
                day, common_parsers.parse_availability_slots, skip_if_empty=True
            )
            if slots is not None:
                teacher_data.availability_slots.append(slots)
        return teacher_data

    @transaction.atomic
    def _create_entity(self, entity_data: TeacherData) -> None:
        try:
            personal_info = self._create_personal_info(entity_data)
            if personal_info is None:
                raise ValueError("Unable to create mandatory data")
            teacher = Teacher.objects.create(
                project_status=entity_data.project_status,
                has_prior_teaching_experience=entity_data.has_prior_teaching_experience,
                peer_support_can_give_feedback=entity_data.peer_support_can_give_feedback,
                simultaneous_groups=entity_data.simultaneous_groups,
                can_host_speaking_club=entity_data.can_host_speaking_club,
                personal_info=personal_info,
                status_since=entity_data.status_since,
                is_validated=entity_data.is_validated,
                weekly_frequency_per_group=entity_data.weekly_frequency_per_group,
                non_teaching_help_provided_comment=entity_data.non_teaching_help_provided_comment,
                has_hosted_speaking_club=entity_data.has_hosted_speaking_club,
                comment=self._create_comment(),
            )
            if entity_data.situational_status is not None:
                teacher.situational_status = entity_data.situational_status
            teacher.student_age_ranges.set(
                self._create_age_ranges(entity_data.is_teaching_children)
            )
            teacher.availability_slots.set(
                self._create_availability_slots(entity_data.availability_slots)
            )
            teacher.teaching_languages_and_levels.set(
                self._create_language_and_levels(entity_data.teaching_languages_and_levels)
            )
            teacher.save()
            self._update_metadata(teacher.personal_info.id, entity_data.id, entity_data.first_name)
            logger.info(
                f"Teacher migrated, old id: {entity_data.id}, new id: {teacher.personal_info.id}"
            )
        except (IntegrityError, TransactionManagementError, ValueError) as e:
            logger.warning(
                f"Teacher with {self.id_name} {entity_data.id} can not be parsed, see errors above"
            )
            logger.debug(e)

    def _create_age_ranges(self, is_teaching_children: bool) -> QuerySetAny[AgeRange, AgeRange]:
        if is_teaching_children:
            return AgeRange.objects.all()
        return AgeRange.objects.filter(age_from__gte=17)

    def _update_metadata(self, new_id: int, old_id: int, name: str) -> None:
        self._metadata[self.entity_name].append({"new_id": new_id, "old_id": old_id, "name": name})


if __name__ == "__main__":
    args = get_args()
    teachers = load_csv_data(args.input_csv)
    populator = TeacherPopulator(teachers, COLUMN_TO_ID, dry=args.dry, logger=logger)
    populator.run()
