import logging
from collections.abc import Iterable
from datetime import datetime

import pytz

from api.models import (
    Coordinator,
    CoordinatorLogEvent,
    Group,
    GroupLogEvent,
    LogEvent,
    Student,
    StudentLogEvent,
    Teacher,
    TeacherLogEvent,
    TeacherUnder18,
    TeacherUnder18LogEvent,
)
from api.models.choices.statuses import Status
from api.models.log_event_rules.log_event_rules import LOG_EVENT_RULES, LogEventResult
from api.models.people import Person

logger = logging.getLogger(__name__)


class LogEventRuleApplier:
    """Class for applying log event rules by creating new log events and/or statuses."""

    @classmethod
    def apply_for_group(  # noqa: PLR0913
        cls,
        log_event: LogEvent,
        coordinators: Iterable[Coordinator] | None = None,
        groups: Iterable[Group] | None = None,
        students: Iterable[Student] | None = None,
        teachers: Iterable[Teacher] | None = None,
        teachers_under_18: Iterable[TeacherUnder18] | None = None,
    ) -> None:
        try:
            rule: LogEventResult = LOG_EVENT_RULES[log_event.type]
        except KeyError:
            logger.warning(
                f"No log event rule found for {log_event.type=}. "
                "This is not necessarily a coding error, but most log events should have"
                "at least some status changes linked to them."
            )
            return

        for coordinator in coordinators:
            CoordinatorLogEvent(
                coordinator=coordinator,
                type=rule.coordinator_log_event_type,
            ).save()
            cls._set_status(coordinator, rule.coordinator_status)
        for group in groups:
            GroupLogEvent(
                group=group,
                type=rule.group_log_event_type,
            ).save()
            cls._set_status(group, rule.group_status)
        for student in students:
            StudentLogEvent(
                student=student,
                type=rule.student_log_event_type,
            ).save()
            cls._set_status(student, rule.student_status)
        for teacher in teachers:
            TeacherLogEvent(
                teacher=teacher,
                type=rule.teacher_log_event_type,
            ).save()
            cls._set_status(teacher, rule.teacher_status)
        for teacher_under_18 in teachers_under_18:
            TeacherUnder18LogEvent(
                teacher_under_18=teacher_under_18,
                type=rule.teacher_under_18_log_event_type,
            ).save()
            cls._set_status(teacher_under_18, rule.teacher_under_18_status)

    @staticmethod
    def _set_status(obj: Group | Person, status: Status) -> None:
        """Sets status, sets `status_since` to current time in UTC, saves object."""
        obj.status = status
        obj.status_since = datetime.now(tz=pytz.UTC)
        obj.save()
