from dataclasses import dataclass

from api.models.choices.log_event_types import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
    TeacherUnder18LogEventType,
)
from api.models.choices.statuses import (
    CoordinatorStatus,
    GroupStatus,
    StudentStatus,
    TeacherStatus,
    TeacherUnder18Status,
)

LogEventType = (
    CoordinatorLogEventType
    | GroupLogEventType
    | StudentLogEventType
    | TeacherLogEventType
    | TeacherUnder18LogEventType
)


@dataclass(frozen=True)
class LogEventResult:
    """Object specifying the statuses to be set and/or types of events to be created.

    A log event leads to some more statuses needing to change and new log events being created.

    E.g. when group finishes studies, the creation of corresponding log event triggers more
    log events and statuses: all students get the status saying they have finished studying,
    a teacher becomes available for a new group.

    Note that objects of this class only specify rules, they don't change statuses or
    create events. So its attributes are not log events, but *types* of log events.
    """

    coordinator_status: CoordinatorStatus | None = None
    coordinator_log_event_type: CoordinatorLogEventType | None = None
    group_status: GroupStatus | None = None
    group_log_event_type: GroupLogEventType | None = None
    student_status: StudentStatus | None = None
    student_log_event_type: StudentLogEventType | None = None
    teacher_status: TeacherStatus | None = None
    teacher_log_event_type: TeacherLogEventType | None = None
    teacher_under_18_status: TeacherUnder18Status | None = None
    teacher_under_18_log_event_type: TeacherUnder18LogEventType | None = None


LOG_EVENT_RULES: dict[LogEventType, LogEventResult] = {
    CoordinatorLogEventType.JOINED: LogEventResult(
        coordinator_status=CoordinatorStatus.ONBOARDING
    ),
}
