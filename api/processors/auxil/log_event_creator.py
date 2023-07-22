import enum

from api.models import CoordinatorLogEvent, Group, GroupLogEvent, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)


class FromOrToGroup(enum.Enum):
    FROM = "from_group"
    TO = "to_group"


class GroupLogEventCreator:
    @staticmethod
    def create(  # noqa: PLR0913
        group: Group,
        group_log_event_type: GroupLogEventType,
        student_log_event_type: StudentLogEventType,
        teacher_log_event_type: TeacherLogEventType,
        coordinator_log_event_type: CoordinatorLogEventType | None = None,
        from_or_to_group: FromOrToGroup = FromOrToGroup.FROM,
    ) -> None:
        GroupLogEvent.objects.create(group=group, type=group_log_event_type)
        if coordinator_log_event_type is not None:
            CoordinatorLogEvent.objects.bulk_create(
                CoordinatorLogEvent(
                    coordinator=coordinator,
                    group=group,
                    type=coordinator_log_event_type,
                )
                for coordinator in group.coordinators.iterator()
            )
        from_or_to_group_arg = {from_or_to_group.value: group}

        StudentLogEvent.objects.bulk_create(
            StudentLogEvent(student=student, type=student_log_event_type, **from_or_to_group_arg)
            for student in group.students.iterator()
        )

        TeacherLogEvent.objects.bulk_create(
            TeacherLogEvent(teacher=teacher, type=teacher_log_event_type, **from_or_to_group_arg)
            for teacher in group.teachers.iterator()
        )
