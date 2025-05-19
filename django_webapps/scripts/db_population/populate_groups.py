import datetime
import os
from dataclasses import dataclass, field
from typing import Any

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()


from django.db import IntegrityError, transaction  # noqa: E402
from django.db.transaction import TransactionManagementError  # noqa: E402
from django.utils import timezone  # noqa: E402

from api.models.choices.communication_language_mode import CommunicationLanguageMode  # noqa: E402
from api.models.choices.status.project import GroupProjectStatus  # noqa: E402
from api.models.coordinator import Coordinator  # noqa: E402
from api.models.group import Group  # noqa: E402
from api.models.language_and_level import LanguageAndLevel  # noqa: E402
from api.models.student import Student  # noqa: E402
from api.models.teacher import Teacher  # noqa: E402
from django_webapps.scripts.db_population.base_populator import (  # noqa: E402
    BasePopulatorFromCsv,
    CsvData,
)
from django_webapps.scripts.db_population.parsers import (  # noqa: E402;
    common_parsers,
    group_parsers,
)
from django_webapps.scripts.db_population.utils import (  # noqa: E402;
    get_logger,
    get_parser,
    load_csv_data,
)

logger = get_logger("groups.log")

COLUMN_TO_ID = {
    "gid": 0,
    "status": 1,
    "free_seats": 2,
    "level": 3,
    "age_group": 4,
    "teacher_language": 5,
    "day_1": 6,
    "time_1": 7,
    "day_2": 8,
    "time_2": 9,
    "day_3": 10,
    "time_3": 11,
    "duration": 12,
    "tid": 13,
    "sid": 14,
    "cid": 15,
    "coordinator_comment": 16,
}


@dataclass
class GroupsData:
    gid: int
    language_level: list[str] = field(default_factory=list)
    teacher_language: list[str] = field(default_factory=list)
    project_status: GroupProjectStatus = GroupProjectStatus.WORKING
    day_1: str | None = None
    time_1: str | None = None
    day_2: str | None = None
    time_2: str | None = None
    day_3: str | None = None
    time_3: str | None = None
    duration: int = 60
    tids: list[int] = field(default_factory=list)
    sids: list[int] = field(default_factory=list)
    cids: list[int] = field(default_factory=list)
    status_since: datetime.datetime = timezone.now()

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, name, None) is not None and value is None:
            return
        super().__setattr__(name, value)


class GroupsPopulator(BasePopulatorFromCsv):
    id_name: str = "gid"
    entity_name: str = "group"

    def _pre_process_data(self, csv_data: CsvData) -> CsvData:
        return super()._pre_process_data(csv_data)

    def _get_entity_data(self) -> GroupsData | None:
        if self._current_entity is None:
            raise TypeError("Value of current group can not be None")
        gid = self._parse_cell("gid", common_parsers.find_digit)
        if gid is None:
            return None
        group_data = GroupsData(gid=gid)
        group_data.day_1 = self._parse_cell(
            "day_1", lambda x: x.strip().rstrip().lower() if x else None
        )
        group_data.day_2 = self._parse_cell(
            "day_2", lambda x: x.strip().rstrip().lower() if x else None
        )
        group_data.day_3 = self._parse_cell(
            "day_3", lambda x: x.strip().rstrip().lower() if x else None
        )
        group_data.time_1 = self._parse_cell("time_1", common_parsers.parse_time_string)
        group_data.time_2 = self._parse_cell("time_2", common_parsers.parse_time_string)
        group_data.time_3 = self._parse_cell("time_3", common_parsers.parse_time_string)
        group_data.duration = self._parse_cell("duration", lambda x: int(x) if x else None)
        group_data.project_status = self._parse_cell("status", group_parsers.parse_status)
        group_data.language_level = self._parse_cell("level", common_parsers.parse_language_level)
        group_data.cids = self._parse_cell("cid", common_parsers.parse_list_of_digits)
        group_data.tids = self._parse_cell("tid", common_parsers.parse_list_of_digits)
        group_data.sids = self._parse_cell("sid", common_parsers.parse_list_of_digits)
        group_data.teacher_language = self._parse_cell(
            "teacher_language",
            group_parsers.parse_languages,
        )
        return group_data

    @transaction.atomic
    def _create_entity(self, entity_data: GroupsData) -> None:
        try:
            fake_language_and_level = self._create_language_and_levels(levels=["A1"]).first()
            if fake_language_and_level is None:
                return

            if Group.objects.filter(legacy_gid=entity_data.gid).count():
                logger.warning(
                    f"Coordinator with {self.id_name} {entity_data.gid} was already migrated"
                )
                return
            group = Group.objects.create(
                legacy_gid=entity_data.gid,
                project_status=entity_data.project_status,
                status_since=entity_data.status_since,
                lesson_duration_in_minutes=entity_data.duration,
                language_and_level=fake_language_and_level,
                friday="08:00",
                comment=self._create_comment(),
            )
            # were needed only to bypass constraint
            group.language_and_level = None  # type: ignore
            group.friday = None

            for day, time in [
                (entity_data.day_1, entity_data.time_1),
                (entity_data.day_2, entity_data.time_2),
                (entity_data.day_3, entity_data.time_3),
            ]:
                if day and time:
                    group = self._add_day(group, day, time)
            group.students.set(Student.objects.filter(legacy_sid__in=entity_data.sids))
            group.teachers.set(Teacher.objects.filter(legacy_tid__in=entity_data.tids))
            group.coordinators.set(Coordinator.objects.filter(legacy_cid__in=entity_data.cids))
            self._add_language_and_level(
                group, entity_data.language_level, entity_data.teacher_language
            )
            self._update_metadata(group.pk, entity_data.gid)
            group = self._add_language_and_level(
                group, entity_data.language_level, entity_data.teacher_language
            )
            group.save()
            logger.info(f"Group migrated, old id: {entity_data.gid}, new id: {group.pk}")
        except (IntegrityError, TransactionManagementError) as e:
            logger.warning(
                f"Group with {self.id_name} {entity_data.gid} can not be parsed, see above"
            )
            logger.debug(e)

    def _add_language_and_level(
        self, group: Group, levels: list[str], languages: list[str]
    ) -> Group:
        levels = [max(levels)] if levels else []
        if not languages:
            return group
        if "Russian" in languages or "English" in languages or "Ukrainian" in languages:
            language_and_level = self._create_language_and_levels(levels).first()
            if language_and_level:
                group.language_and_level = language_and_level
            if "Russian" in languages and "Ukrainian" in languages:
                group.communication_language_mode = CommunicationLanguageMode.RU_OR_UA
            elif "Russian" in languages:
                group.communication_language_mode = CommunicationLanguageMode.RU_ONLY
            elif "Ukrainian" in languages:
                group.communication_language_mode = CommunicationLanguageMode.UA_ONLY
            else:
                group.communication_language_mode = CommunicationLanguageMode.L2_ONLY
            return group

        # then choose only one
        qs = LanguageAndLevel.objects.filter(language__name=languages[0])
        if levels:
            qs = qs.filter(level_id__in=levels)
        language_and_level = qs.first()
        if language_and_level:
            group.language_and_level = language_and_level
        group.communication_language_mode = CommunicationLanguageMode.RU_ONLY
        return group

    def _add_day(self, group: Group, day: str, time: str) -> Group:
        if day == "понедельник":
            group.monday = time
        elif day == "вторник":
            group.tuesday = time
        elif day == "среда":
            group.wednesday = time
        elif day == "четверг":
            group.thursday = time
        elif day == "пятница":
            group.friday = time
        elif day == "субота":
            group.saturday = time
        elif day == "воскресенье":
            group.sunday = time
        return group

    def _update_metadata(self, new_id: int, old_id: int) -> None:
        self._metadata[self.entity_name].append({"new_id": new_id, "old_id": old_id})


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    groups = load_csv_data(args.input_csv)
    # Group.objects.all().delete()
    populator = GroupsPopulator(
        # groups[1:],
        groups,
        COLUMN_TO_ID,
        dry=args.dry,
        logger=logger,
    )
    populator.run()
