import datetime
import os
from dataclasses import dataclass

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")
django.setup()

from django.db import IntegrityError, transaction  # noqa: E402
from django.db.transaction import TransactionManagementError  # noqa: E402
from django.utils import timezone  # noqa: E402

from api.models.choices.status.project import CoordinatorProjectStatus  # noqa: E402
from api.models.coordinator import Coordinator  # noqa: E402
from devtools.scripts.db_population.base_populator import (  # noqa: E402
    BasePersonEntityData,
    BasePopulatorFromCsv,
    CsvData,
)
from devtools.scripts.db_population.parsers import common_parsers  # noqa: E402
from devtools.scripts.db_population.utils import get_args, get_logger, load_csv_data  # noqa: E402

logger = get_logger("coordinators.log")
LIST_OF_ADMINS_IDS = [1, 22, 39, 42, 225, 238, 208]

COLUMN_TO_ID = {
    "cid": 0,
    "name": 1,
    "email": 2,
    "tg": 3,
    "timezone": 4,
}


@dataclass
class CoordinatorData(BasePersonEntityData):
    project_status: CoordinatorProjectStatus = CoordinatorProjectStatus.WORKING_OK
    last_name: str = ""
    is_validated: bool = True
    is_admin: bool = False
    utc_timedelta: datetime.timedelta = datetime.timedelta(hours=0)
    status_since: datetime.datetime = timezone.now()


class CoordinatorPopulator(BasePopulatorFromCsv):
    id_name: str = "cid"
    entity_name: str = "coordinator"

    def _pre_process_data(self, csv_data: CsvData, reverse: bool = False) -> CsvData:
        self.header[1] = "name"
        self.header[4] = "timezone"
        csv_data = csv_data[2:]
        return super()._pre_process_data(csv_data, reverse)

    def _get_entity_data(self) -> CoordinatorData | None:
        if self._current_entity is None:
            raise TypeError("Value of current teacher can not be None")
        entity_id = int(self._current_entity[self._column_to_id[self.id_name]])
        name = self._parse_cell("name", common_parsers.parse_name)
        telegram_username = self._parse_cell("tg", common_parsers.parse_telegram_name)
        email = self._parse_cell("email", common_parsers.parse_email)
        coordinator_data = CoordinatorData(
            email=email,
            first_name=name,
            telegram_username=telegram_username,
            id=entity_id,
            is_admin=entity_id in LIST_OF_ADMINS_IDS,
        )
        timezone = self._parse_cell("timezone", common_parsers.parse_timezone, skip_if_empty=True)
        coordinator_data.utc_timedelta = timezone.utcoffset(None) if timezone else None
        return coordinator_data

    @transaction.atomic
    def _create_entity(self, entity_data: CoordinatorData) -> None:
        logger.debug(
            f"-> Начинаем миграцию координатора: legacy_id={entity_data.id}, "
            f"name={entity_data.first_name!r}, email={entity_data.email!r}"
        )
        try:
            personal_info = self._create_personal_info(entity_data)
            logger.debug(f"   personal_info создано: {personal_info!r}")

            if personal_info is None:
                logger.warning(f"   personal_info пустое, пропускаем legacy_id={entity_data.id}")
                return
            exists = Coordinator.objects.filter(legacy_cid=entity_data.id).exists()
            logger.debug(
                f"   проверка существования в БД (legacy_cid={entity_data.id}) -> {exists}"
            )
            if exists:
                logger.warning(f"   уже мигрирован, пропускаем legacy_id={entity_data.id}")
                return

            coordinator = Coordinator.objects.create(
                legacy_cid=entity_data.id,
                project_status=entity_data.project_status,
                personal_info=personal_info,
                is_admin=entity_data.is_admin,
                is_validated=entity_data.is_validated,
                status_since=entity_data.status_since,
                comment=self._create_comment(),
            )
            logger.debug(f"   Coordinator.objects.create -> {coordinator!r}")
            coord_id = coordinator.personal_info.id
            self._update_metadata(
                coordinator.personal_info.id, entity_data.id, entity_data.first_name
            )
            logger.info(f"Coordinator migrated, old id: {entity_data.id}, new id: {coord_id}")
        except (IntegrityError, TransactionManagementError) as e:
            logger.warning(
                f"Coordinator with {self.id_name} {entity_data.id} can not be parsed, see above"
            )
            logger.debug(e)
            logger.error(f"Ошибка при миграции legacy_id={entity_data.id}: {e!r}", exc_info=True)

    def _update_metadata(self, new_id: int, old_id: int, name: str) -> None:
        self._metadata[self.entity_name].append({"new_id": new_id, "old_id": old_id, "name": name})


if __name__ == "__main__":
    args = get_args()
    teachers = load_csv_data(args.input_csv)
    populator = CoordinatorPopulator(teachers, COLUMN_TO_ID, dry=args.dry, logger=logger)
    logger.debug(
        f"Запуск популятора (dry-run={args.dry}) с {len(teachers)} строками из {args.input_csv}"
    )
    populator.run()
    logger.info("=== Миграция координаторов завершена ===")
