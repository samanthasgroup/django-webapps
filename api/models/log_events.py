from django.db import models

from api.models.auxil import InternalModelWithName
from api.models.people import Coordinator, Student, Teacher

# We could have created one table listing all possible names of log events, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class CoordinatorLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a coordinator."""


class GroupLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a group."""


class StudentLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a student."""


class TeacherLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a teacher."""


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


class GroupLogEvent(LogEvent):
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    name = models.ForeignKey(GroupLogEventName, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date_as_str}: group {self.group} {self.name}"


class CoordinatorLogEvent(PersonLogEvent):
    name = models.ForeignKey(CoordinatorLogEventName, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.date_as_str}: coordinator {self.coordinator.personal_info.full_name} "
            f"{self.name}"
        )


class StudentLogEvent(PersonLogEvent):
    name = models.ForeignKey(StudentLogEventName, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date_as_str}: student {self.student.personal_info.full_name} {self.name}"


class TeacherLogEvent(PersonLogEvent):
    name = models.ForeignKey(TeacherLogEventName, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date_as_str}: teacher {self.teacher.personal_info.full_name} {self.name}"
