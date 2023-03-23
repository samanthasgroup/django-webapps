from django.db import models

from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.groups import Group
from api.models.people import Coordinator, Student, Teacher, TeacherUnder18

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

    class EventType(models.TextChoices):
        APPLIED = "applied", "Applied for the role"
        JOINED = "joined", "Joined the team"
        STARTED_ONBOARDING = "onboarding_start", "Started onboarding"
        FINISHED_ONBOARDING = "onboarding_end", "Finished onboarding"
        TOOK_NEW_GROUP = (
            "took_new_group",
            "Took a new group (not transferred from another coordinator)",
        )
        GROUP_STARTED_CLASSES = "group_started_classes", "The group started classes"
        REQUESTED_TRANSFER = (
            "requested_transfer",
            "Requested that the group be transferred to a different coordinator",
        )
        TRANSFER_CANCELED = (
            "transfer_canceled",
            "Transfer canceled (declined or the coordinator changed their mind)",
        )
        TRANSFER_COMPLETED = "transferred", "Transfer of group to another coordinator completed"
        TOOK_TRANSFERRED_GROUP = "took_transfer", "Received group from another coordinator"
        REQUESTED_LEAVE = "requested_leave", "Requested a leave"
        LEAVE_CONFIRMED = "leave_confirmed", "Leave confirmed"
        RETURNED_FROM_LEAVE = "returned_from_leave", "Returned from leave"
        DECLINED = "declined_to_continue", "Declined to continue participating in the project"
        FINISHED_AND_LEAVING = (
            "finished_and_leaving",
            "Finished working and announced that they are leaving the project",
        )
        FINISHED_AND_STAYING = (
            "finished_and_staying",
            "Finished working and announced that they are staying in the project",
        )
        ACCESS_REVOKED = "access_revoked", "Access to corporate resources revoked"

    coordinator = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        related_name="coordinator_log_events",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
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

    class EventType(models.TextChoices):
        FORMED = "formed", "Formed (automatically or by coordinator)"
        NOT_CONFIRMED_TEACHER_REFUSED = (
            "not_confirmed_teacher",
            "Not confirmed because teacher refused",
        )
        NOT_CONFIRMED_NOT_ENOUGH_STUDENTS = (
            "not_confirmed_students",
            "Not confirmed because not enough students confirmed their participation",
        )
        CONFIRMED = "confirmed", "Confirmed"
        STARTED = "started", "Started classes"
        ABORTED = "aborted", "Finished prematurely"
        FINISHED = "finished", "Finished successfully"
        COORDINATOR_REQUESTED_TRANSFER = (
            "coordinator_requested_transfer",
            "Coordinator requested transfer of group to another coordinator",
        )
        STUDENT_REQUESTED_TRANSFER = (
            "student_requested_transfer",
            "Student requested transfer to another group",
        )
        TEACHER_REQUESTED_SUBSTITUTION = (
            "teacher_requested_substitution",
            "Teacher requested to be substituted with another teacher",
        )

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
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

    class EventType(models.TextChoices):
        REGISTERED = "registered", "Completed registration"
        AWAITING_OFFER = "awaiting_offer", "Registration complete, waiting for a group"
        GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
        ACCEPTED_OFFER = "accepted_offer", "Was offered a group and accepted it"
        DECLINED_OFFER = "declined_offer", "Was offered a group but declined it"
        GROUP_CONFIRMED = "group_confirmed", "Group confirmed, awaiting start of classes"
        STUDY_START = "start", "Started studying in a group"
        MISSED_CLASS_NOTIFIED = (
            "missed_class_notified",
            "Missed a class but let the teacher know in advance",
        )
        MISSED_CLASS_SILENTLY = (
            "missed_class_silently",
            "Missed a class without letting the teacher know in advance",
        )
        REQUESTED_TRANSFER = "requested_transfer", "Requested transfer"
        TRANSFERRED = "transferred", "Transferred"
        TRANSFER_CANCELED = "transfer_canceled", "Transfer canceled"
        ABORTED = "aborted", "Left the project prematurely"
        FINISHED_LEFT = "finished_left", "Completed the course and left the project"
        FINISHED_STAYS = "finished_stays", "Completed the course and wants to join another group"

    from_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="student_log_events_from_this_group",
    )
    to_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="student_log_events_to_this_group",
    )
    student = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
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

    class EventType(models.TextChoices):
        REGISTERED = "registered", "Completed registration"
        JOINED = "joined", "Joined the team"
        AWAITING_OFFER = (
            "awaiting_offer",
            "Registration and validation complete, started waiting for a group",
        )
        GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
        ACCEPTED_OFFER = "accepted_offer", "Was offered a group and accepted it"
        DECLINED_OFFER = "declined_offer", "Was offered a group but declined it"
        GROUP_CONFIRMED = "group_confirmed", "Group confirmed, awaiting start of classes"
        STUDY_START = "start", "Started teaching a group"
        REQUESTED_TRANSFER = "requested_transfer", "Requested transfer"
        TRANSFERRED = "transferred", "Transferred"
        TRANSFER_CANCELED = "transfer_canceled", "Transfer canceled"
        ABORTED = "aborted", "Left the project prematurely"
        FINISHED_LEFT = "finished_left", "Completed the course and left the project"
        FINISHED_STAYS = "finished_stays", "Completed the course and wants to join another group"

    from_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="teacher_log_events_from_this_group",
    )
    to_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="teacher_log_events_to_this_group",
    )
    teacher = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
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

    class EventType(models.TextChoices):
        REGISTERED = "registered", "Completed registration"
        JOINED = "joined", "Joined the team"
        LEFT = "left", "Left the project"

    teacher = models.ForeignKey(TeacherUnder18, related_name="log", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=EventType.choices
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
