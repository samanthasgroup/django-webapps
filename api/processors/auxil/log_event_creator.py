from api.models import CoordinatorLogEvent, Group, GroupLogEvent, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)


class GroupLogEventCreator:
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
