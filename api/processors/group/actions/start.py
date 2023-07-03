import datetime

from django.db import transaction

from api.models import Group, Teacher
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import GroupStatus, StudentStatus, TeacherStatus
from api.processors.group.actions.base import (
    BaseActionProcessor,
    CommonCoordinatorsStatusSetter,
    CommonLogEventsCreator,
)


class StartProcessor(BaseActionProcessor):
    @transaction.atomic
    def process(self, group: Group) -> None:
        self._create_log_events(group)
        self._set_statuses(group, group_status=GroupStatus.WORKING)

    def _create_log_events(self, group: Group) -> None:
        CommonLogEventsCreator.create(
            group=group,
            student_log_event_type=StudentLogEventType.STUDY_START,
            teacher_log_event_type=TeacherLogEventType.STUDY_START,
            coordinator_log_event_type=CoordinatorLogEventType.TOOK_NEW_GROUP,
            group_log_event_type=GroupLogEventType.STARTED,
        )

    def _set_students_status(self, group: Group, timestamp: datetime.datetime) -> None:
        group.students.update(
            status=StudentStatus.STUDYING,
            status_since=timestamp,
        )

    def _set_teachers_status(self, timestamp: datetime.datetime) -> None:
        teachers = Teacher.objects

        teachers.filter_can_take_more_groups().update(
            status=TeacherStatus.TEACHING_ACCEPTING_MORE,
            status_since=timestamp,
        )

        teachers.filter_cannot_take_more_groups().update(
            status=TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            status_since=timestamp,
        )

    def _set_coordinators_status(self, timestamp: datetime.datetime) -> None:
        CommonCoordinatorsStatusSetter.set(timestamp)
