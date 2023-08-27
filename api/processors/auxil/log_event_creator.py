from api.models import CoordinatorLogEvent, Group, GroupLogEvent, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)


class GroupLogEventCreator:
    @staticmethod
    def create(  # noqa: PLR0913
        group: Group,
        student_log_event_type: StudentLogEventType,
        teacher_log_event_type: TeacherLogEventType,
        group_log_event_type: GroupLogEventType | None = None,
        coordinator_log_event_type: CoordinatorLogEventType | None = None,
        from_group: Group | None = None,
        to_group: Group | None = None,
        comment: str = "",
    ) -> None:
        if group_log_event_type is not None:
            GroupLogEvent.objects.create(group=group, type=group_log_event_type, comment=comment)
        if coordinator_log_event_type is not None:
            CoordinatorLogEvent.objects.bulk_create(
                CoordinatorLogEvent(
                    coordinator=coordinator,
                    group=group,
                    type=coordinator_log_event_type,
                    comment=comment,
                )
                for coordinator in group.coordinators.iterator()
            )

        StudentLogEvent.objects.bulk_create(
            StudentLogEvent(
                student=student,
                type=student_log_event_type,
                from_group=from_group,
                to_group=to_group,
                comment=comment,
            )
            for student in group.students.iterator()
        )

        TeacherLogEvent.objects.bulk_create(
            TeacherLogEvent(
                teacher=teacher,
                type=teacher_log_event_type,
                from_group=from_group,
                to_group=to_group,
                comment=comment,
            )
            for teacher in group.teachers.iterator()
        )
