import datetime
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from django.db import IntegrityError, transaction
from django_stubs_ext import QuerySetAny
from tqdm import tqdm

from api.models.day_and_time_slot import DayAndTimeSlot
from api.models.language_and_level import LanguageAndLevel
from api.models.personal_info import PersonalInfo

CsvData = list[list[str]]
ParseCellReturnType = TypeVar("ParseCellReturnType")
EntityDataType = TypeVar("EntityDataType", bound="BasePersonEntityData")


@dataclass
class BasePersonEntityData:
    id: int
    first_name: str
    email: str
    telegram_username: str = ""
    last_name: str = ""
    utc_timedelta: datetime.timedelta = datetime.timedelta(hours=0)
    phone_number: str | None = None

    # use default values
    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, name, None) is not None and value is None:
            return
        super().__setattr__(name, value)


class BasePersonPopulatorFromCsv(ABC):
    entity_name: str = "abstract_entity"
    id_name: str = "aid"

    def __init__(  # noqa: PLR0913
        self,
        csv_data: CsvData,
        column_to_id: dict[str, int],
        dry: bool = False,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self._column_to_id = column_to_id
        self.header = csv_data[0]
        self.csv_data = self._pre_process_data(csv_data[1:])
        self._logger = logger
        self._dry = dry
        self._current_entity = None
        self._current_entity_id = None

    def run(self) -> None:
        for entity in tqdm(self.csv_data, desc=f"Processing {self.entity_name}s..."):
            self._current_entity_id = entity[self._column_to_id[self.id_name]]
            self._logger.info("======================================================= ")
            self._logger.info(
                f"Parsing {self.entity_name} with {self.id_name} {self._current_entity_id}"
            )
            self._current_entity = entity

            entity_data = self._get_entity_data()
            if entity_data is None:
                continue

            if not self._dry:
                self._create_entity(entity_data)

    @abstractmethod
    def _pre_process_data(self, csv_data: CsvData) -> CsvData:
        self.header[0] = self.id_name
        csv_data.sort(key=lambda entity: int(entity[self._column_to_id[self.id_name]]))
        return csv_data

    @abstractmethod
    def _get_entity_data(self) -> Any | None:
        pass

    @transaction.atomic
    @abstractmethod
    def _create_entity(self, entity_data: Any) -> None:
        pass

    def _report_error(self, error: ValueError) -> None:
        self._logger.error(f"{self._current_entity_id}: {error}")

    def _report_warning(self, column_name: str, value: str) -> None:
        message = f"{self._current_entity_id}: {column_name} can not be parsed, value: {value}"
        self._logger.warning(message)

    def _parse_cell(
        self,
        column_name: str,
        parser: Callable[..., ParseCellReturnType],
        skip_if_empty: bool = False,
    ) -> ParseCellReturnType | None:
        if self._current_entity is None:
            raise TypeError(f"Value of current {self.entity_name} can not be None")
        index = self._column_to_id[column_name]
        if skip_if_empty and self._current_entity[index].strip() == "":
            return None
        try:
            result = parser(self._current_entity[index])
            if result is None or (isinstance(result, list) and len(result) == 0):
                self._report_warning(self.header[index], self._current_entity[index])
            return result
        except ValueError as error:
            self._report_error(error)
        return None

    def _create_personal_info(self, entity_data: EntityDataType) -> None | PersonalInfo:
        if (
            entity_data.first_name is None
            or entity_data.telegram_username is None
            or entity_data.email is None
        ):
            return None
        try:
            return PersonalInfo.objects.create(
                first_name=entity_data.first_name,
                last_name=entity_data.last_name,
                telegram_username=entity_data.telegram_username,
                email=entity_data.email,
                utc_timedelta=entity_data.utc_timedelta,
                phone=entity_data.phone_number,
            )
        except IntegrityError as _:
            self._logger.warning(
                f"{self._current_entity_id}: {self.entity_name} might be a duplicate"
            )
        return None

    def _create_language_and_levels(
        self, levels: list[str]
    ) -> QuerySetAny[LanguageAndLevel, LanguageAndLevel]:
        qs = LanguageAndLevel.objects.filter(language__name="English")
        if levels:
            qs = qs.filter(level_id__in=levels)
        return qs

    def _create_availability_slots(
        self, weekly_slots: list[list[tuple[int, int]]]
    ) -> list[DayAndTimeSlot]:
        result: list[DayAndTimeSlot] = []
        for day_index, slots in enumerate(weekly_slots):
            for from_hour, to_hour in slots:
                result.extend(
                    DayAndTimeSlot.objects.filter(
                        day_of_week_index=day_index,
                        time_slot__from_utc_hour=datetime.time(hour=from_hour),
                        time_slot__to_utc_hour=datetime.time(hour=to_hour),
                    )
                )
        return result

    def _create_comment(self) -> str:
        if self._current_entity is None:
            raise TypeError(f"Value of current {self.entity_name} can not be None")
        rows = ["======= OLD CSV DATA ======="]
        for index in self._column_to_id.values():
            rows.append(f"{self.header[index]} - {self._current_entity[index]}\n")
        rows.append("======= END OF OLD CSV DATA =======")
        return "\n".join(rows)
