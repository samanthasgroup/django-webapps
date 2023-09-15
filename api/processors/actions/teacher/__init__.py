import abc

from django.db import transaction
from django.utils import timezone

from api.models import Teacher


class TeacherActionProcessor(abc.ABC):
    def __init__(self, teacher: Teacher):
        self.teacher = teacher
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
