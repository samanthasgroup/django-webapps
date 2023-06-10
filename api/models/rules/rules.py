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
class Result:
    coordinator_status: CoordinatorStatus | None = None
    group_status: GroupStatus | None = None
    student_status: StudentStatus | None = None
    teacher_status: TeacherStatus | None = None
    teacher_under_18_status: TeacherUnder18Status | None = None


RULES: dict[LogEventType, Result] = {
    CoordinatorLogEventType.JOINED: Result(coordinator_status=CoordinatorStatus.ONBOARDING),
}
