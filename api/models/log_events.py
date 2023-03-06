from django.db import models

from api.models.base import InternalModelWithName
from api.models.group import Group
from api.models.people import Coordinator, Student, Teacher

# We could have created one table listing all possible names of log events, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class CoordinatorLogEventType(InternalModelWithName):
    """Model for enumeration of possible types of log events (events) for a coordinator."""


class GroupLogEventType(InternalModelWithName):
    """Model for enumeration of possible types of log events (events) for a group."""


class StudentLogEventType(InternalModelWithName):
    """Model for enumeration of possible types of log events (events) for a student."""


class TeacherLogEventType(InternalModelWithName):
    """Model for enumeration of possible types of log events (events) for a teacher."""


class LogEvent(models.Model):
    """Abstract model for some sort of internal event, e.g. 'joined group' for a
    student or 'finished' for a group. Statuses will be assigned based on these events.

    We don't call the class simply Event for it not to be confused with possible models for events
    organized by the school.
    """

    date_time = models.DateTimeField(auto_now_add=True)

    @property
    def date_as_str(self) -> str:
        return f"{self.date_time.strftime('%d.%m.%Y')}"

    class Meta:
        abstract = True


class GroupLogEvent(LogEvent):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    type = models.ForeignKey(GroupLogEventType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date_as_str}: group {self.group} {self.type.name_for_user}"


class PersonLogEvent(LogEvent):
    """Abstract class for a log event concerning a person."""

    from_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_from_self",  # will produce e.g. "studentLogEvents_from_self"
    )
    to_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_to_self",
    )

    class Meta:
        abstract = True


class CoordinatorLogEvent(PersonLogEvent):
    coordinator = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)
    type = models.ForeignKey(CoordinatorLogEventType, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.date_as_str}: coordinator {self.coordinator.personal_info.full_name} "
            f"{self.type.name_for_user}"
        )


class StudentLogEvent(PersonLogEvent):
    student = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)
    type = models.ForeignKey(StudentLogEventType, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.date_as_str}: student {self.student.personal_info.full_name} "
            f"{self.type.name_for_user}"
        )


class TeacherLogEvent(PersonLogEvent):
    teacher = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)
    type = models.ForeignKey(TeacherLogEventType, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.date_as_str}: teacher {self.teacher.personal_info.full_name} "
            f"{self.type.name_for_user}"
        )
