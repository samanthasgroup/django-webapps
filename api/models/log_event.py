from django.db import models

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
    TeacherUnder18LogEventType,
)
from api.models.coordinator import Coordinator
from api.models.group import Group
from api.models.student import Student
from api.models.teacher import Teacher
from api.models.teacher_under_18 import TeacherUnder18

# We could have created one table listing all possible names of log events, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class LogEvent(models.Model):
    """Abstract model for some sort of internal event.

    This can be e.g. 'joined group' for a student or 'finished' for a group.
    Statuses will be assigned based on these events.

    We don't call the class simply Event for it not to be confused with possible models for events
    organized by the school.
    """

    comment = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def date_as_str(self) -> str:
        return self.date_time.strftime("%d.%m.%Y")


class CoordinatorLogEvent(LogEvent):
    """Model for a log event concerning a coordinator."""

    coordinator = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        related_name="coordinator_log_events",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CoordinatorLogEventType.choices,
    )

    class Meta:
        indexes = [
            models.Index(fields=("coordinator_id",), name="coordinator_id_idx"),
            models.Index(fields=("type",), name="coordinator_log_event_type_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.date_as_str}: coordinator {self.coordinator.personal_info.full_name} "
            f"{self.get_type_display()}"
        )


class GroupLogEvent(LogEvent):
    """Model for a log event concerning a group."""

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=GroupLogEventType.choices,
    )

    class Meta:
        indexes = [
            models.Index(fields=("group_id",), name="group_id_idx"),
            models.Index(fields=("type",), name="group_log_event_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.date_as_str}: group {self.group} {self.get_type_display()}"


class StudentLogEvent(LogEvent):
    """Model for a log event concerning a student."""

    from_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="student_log_events_from_this_group",
    )
    to_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="student_log_events_to_this_group",
    )
    student = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=StudentLogEventType.choices
    )

    class Meta:
        indexes = [
            models.Index(fields=("student_id",), name="student_id_idx"),
            models.Index(fields=("type",), name="student_log_event_type_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.date_as_str}: student {self.student.personal_info.full_name} "
            f"{self.get_type_display()}"
        )


class TeacherLogEvent(LogEvent):
    """Model for a log event concerning an adult teacher."""

    from_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="teacher_log_events_from_this_group",
    )
    to_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="teacher_log_events_to_this_group",
    )
    teacher = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherLogEventType.choices,
    )

    class Meta:
        indexes = [
            models.Index(fields=("teacher_id",), name="young_teacher_id_idx"),
            models.Index(fields=("type",), name="young_teach_log_event_type_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.date_as_str}: teacher {self.teacher.personal_info.full_name} "
            f"{self.get_type_display()}"
        )


class TeacherUnder18LogEvent(LogEvent):
    """Model for a log event concerning a young teacher."""

    teacher = models.ForeignKey(TeacherUnder18, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherUnder18LogEventType.choices,
    )

    class Meta:
        indexes = [
            models.Index(fields=("teacher_id",), name="teacher_id_idx"),
            models.Index(fields=("type",), name="teacher_log_event_type_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.date_as_str}: young teacher {self.teacher.personal_info.full_name} "
            f"{self.get_type_display()}"
        )
