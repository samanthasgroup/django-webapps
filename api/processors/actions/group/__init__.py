import abc

from django.db import transaction
from django.utils import timezone

from api.models import Group


class GroupActionProcessor(abc.ABC):
    def __init__(self, group: Group):
        self.group = group
        self.timestamp = timezone.now()

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._set_statuses()

    @abc.abstractmethod
    def _create_log_events(self) -> None:
        pass

    def _set_statuses(self) -> None:
        self._set_group_status()

        self._set_coordinators_status()
        self._set_students_status()
        self._set_teachers_status()

    @abc.abstractmethod
    def _set_coordinators_status(self) -> None:
        pass

    @abc.abstractmethod
    def _set_group_status(self) -> None:
        pass

    @abc.abstractmethod
    def _set_students_status(self) -> None:
        pass

    @abc.abstractmethod
    def _set_teachers_status(self) -> None:
        pass
