import abc
import datetime

from django.utils import timezone

from api.models import (
    Coordinator,
    CoordinatorLogEvent,
    Group,
    GroupLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
)
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import CoordinatorStatus, GroupStatus
from api.processors.base import Processor


class BaseActionProcessor(Processor):
    def _set_statuses(self, group: Group, group_status: GroupStatus) -> None:
        timestamp = timezone.now()

        self._set_status(obj=group, status=group_status, status_since=timestamp)

        self._set_coordinators_status(timestamp)
        self._set_students_status(group=group, timestamp=timestamp)
        self._set_teachers_status(timestamp)

    @abc.abstractmethod
    def _create_log_events(self, group: Group) -> None:
        pass

    @abc.abstractmethod
    def _set_students_status(self, group: Group, timestamp: datetime.datetime) -> None:
        pass

    @abc.abstractmethod
    def _set_teachers_status(self, timestamp: datetime.datetime) -> None:
        pass

    @abc.abstractmethod
    def _set_coordinators_status(self, timestamp: datetime.datetime) -> None:
        pass

    @abc.abstractmethod
    def process(self, group: Group) -> None:
        pass


class CommonCoordinatorsStatusSetter:
    @staticmethod
    def set(timestamp: datetime.datetime) -> None:
        coordinators = Coordinator.objects

        coordinators.filter_below_threshold().update(
            status=CoordinatorStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.filter_above_threshold_and_within_limit().update(
            status=CoordinatorStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.filter_limit_reached().update(
            status=CoordinatorStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )


class CommonLogEventsCreator:
    @staticmethod
    def create(
        group: Group,
        group_log_event_type: GroupLogEventType,
        student_log_event_type: StudentLogEventType,
        teacher_log_event_type: TeacherLogEventType,
        coordinator_log_event_type: CoordinatorLogEventType,
    ) -> None:
        GroupLogEvent.objects.create(group=group, type=group_log_event_type)

        CoordinatorLogEvent.objects.bulk_create(
            CoordinatorLogEvent(
                coordinator=coordinator,
                group=group,
                type=coordinator_log_event_type,
            )
            for coordinator in group.coordinators.iterator()
        )

        StudentLogEvent.objects.bulk_create(
            StudentLogEvent(student=student, from_group=group, type=student_log_event_type)
            for student in group.students.iterator()
        )

        TeacherLogEvent.objects.bulk_create(
            TeacherLogEvent(teacher=teacher, from_group=group, type=teacher_log_event_type)
            for teacher in group.teachers.iterator()
        )
