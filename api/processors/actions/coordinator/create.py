from django.db import transaction

from api.models import Coordinator
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.models.log_event import CoordinatorLogEvent
from api.processors.actions.coordinator import CoordinatorActionProcessor


class CoordinatorCreateProcessor(CoordinatorActionProcessor):
    def __init__(self, coordinator: Coordinator):
        super().__init__(coordinator)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()

    def _set_statuses(self) -> None:
        return super()._set_statuses()

    def _create_log_events(self) -> None:
        CoordinatorLogEvent.objects.create(
            coordinator=self.coordinator, type=CoordinatorLogEventType.APPLIED
        )
