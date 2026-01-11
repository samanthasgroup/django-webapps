import abc

from django.db import transaction
from django.utils import timezone

from api.models import Group
from api.models.auxil.status_setter import StatusSetter


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
        StatusSetter.update_related_statuses_for_group(self.group, self.timestamp)

    def _move_related_people_to_former(self) -> None:
        teachers_current, students_current, coordinators_current = (
            self.group.teachers,
            self.group.students,
            self.group.coordinators,
        )
        self.group.teachers_former.add(*teachers_current.all())
        self.group.students_former.add(*students_current.all())
        self.group.coordinators_former.add(*coordinators_current.all())
        self.group.teachers.clear()
        self.group.students.clear()
        self.group.coordinators.clear()

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
