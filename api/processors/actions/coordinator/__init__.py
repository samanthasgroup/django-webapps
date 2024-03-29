import abc

from django.db import transaction
from django.utils import timezone

from api.models import Coordinator


class CoordinatorActionProcessor(abc.ABC):
    def __init__(self, coordinator: Coordinator):
        self.coordinator = coordinator
        self.timestamp = timezone.now()

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._set_statuses()

    @abc.abstractmethod
    def _create_log_events(self) -> None:
        pass

    @abc.abstractmethod
    def _set_statuses(self) -> None:
        pass
