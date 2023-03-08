from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.groups import Group
from api.models.people import Coordinator, Student, Teacher

# We could have created one table listing all possible names of log events, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class LogEvent(models.Model):
    """Abstract model for some sort of internal event, e.g. 'joined group' for a
    student or 'finished' for a group. Statuses will be assigned based on these events.

    We don't call the class simply Event for it not to be confused with possible models for events
    organized by the school.
    """

    date_time = models.DateTimeField(auto_now_add=True)

    @property
    def date_as_str(self) -> str:
        return self.date_time.strftime("%d.%m.%Y")

    class Meta:
        abstract = True


class GroupLogEvent(LogEvent):
    class EventType(models.TextChoices):
        FORMED = "formed", "Formed"
        CONFIRMED = "confirmed", "Confirmed"
        STARTED = "started", "Started classes"
        FINISHED = "finished", "Finished classes"
        # TODO put types here once they are finalized

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
    )

    class Meta:
        indexes = [
            models.Index(fields=("group_id",), name="group_id_idx"),
            models.Index(fields=("type",), name="group_log_event_type_idx"),
        ]

    def __str__(self):
        return f"{self.date_as_str}: group {self.group} {self.get_type_display()}"


class PersonLogEvent(LogEvent):
    """Abstract class for a log event concerning a person."""

    from_group = models.ForeignKey(
        "Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_from_self",  # will produce e.g. "studentLogEvents_from_self"
    )
    to_group = models.ForeignKey(
        "Group",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_to_self",
    )

    class Meta:
        abstract = True


class CoordinatorLogEvent(PersonLogEvent):
    class EventType(models.TextChoices):
        JOINED = "joined", "Joined the team"
        STARTED_ONBOARDING = "onboard", "Started onboarding"
        FINISHED_ONBOARDING = "onboard_end", "Finished onboarding"
        TOOK_GROUP = "took_group", "Took a group"
        # TODO put types here once they are finalized

    coordinator = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
    )

    class Meta:
        indexes = [
            models.Index(fields=("coordinator_id",), name="coordinator_id_idx"),
            models.Index(fields=("type",), name="coordinator_log_event_type_idx"),
        ]

    def __str__(self):
        return (
            f"{self.date_as_str}: coordinator {self.coordinator.personal_info.full_name} "
            f"{self.get_type_display()}"
        )


class StudentLogEvent(PersonLogEvent):
    class EventType(models.TextChoices):
        REGISTERED = "register", "Joined the team"
        STUDY_START = "start", "Started studying in a group"
        TRANSFER_REQUEST = "req_transf", "Requested transfer"
        TRANSFER_OK = "transferred", "Transferred"
        MISS_CLASS = "missed_class", "Missed a class"
        STUDY_FINISH = "finish_group", "Finished studying in a group"
        NO_REPLY = "no_reply", "Not replying"
        # TODO put types here once they are finalized

    student = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
    )

    class Meta:
        indexes = [
            models.Index(fields=("student_id",), name="student_id_idx"),
            models.Index(fields=("type",), name="student_log_event_type_idx"),
        ]

    def __str__(self):
        return (
            f"{self.date_as_str}: student {self.student.personal_info.full_name} "
            f"{self.get_type_display()}"
        )


class TeacherLogEvent(PersonLogEvent):
    class EventType(models.TextChoices):
        REGISTERED = "register", "Joined the team"
        STUDY_START = "start", "Started studying in a group"
        STUDY_FINISH = "finish_group", "Finished studying in a group"
        NO_REPLY = "no_reply", "Not replying"
        # TODO put types here once they are finalized

    teacher = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
    )

    class Meta:
        indexes = [
            models.Index(fields=("teacher_id",), name="teacher_id_idx"),
            models.Index(fields=("type",), name="teacher_log_event_type_idx"),
        ]

    def __str__(self):
        return (
            f"{self.date_as_str}: teacher {self.teacher.personal_info.full_name} "
            f"{self.get_type_display()}"
        )
