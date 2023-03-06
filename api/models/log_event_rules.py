from django.db import models

from api.models.base import InternalModelWithName
from api.models.log_events import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)

JSON_HELP_TEXT = "JSON describing what object must get what status when the event is triggered"


# 1. ForeignKeys cannot point to abstract models, and we need these tables to be separate for
#    coordinators' convenience.  Hence these multiple imports and classes.
# 2. I'm subclassing rules from InternalModelWithName because it can be convenient to add a name
#    to the rule so that coordinators understand what it does.
# 3. Note that I match log event types, not log events. One event is an occurrence of event with a
#    timestamp, while rules must be based on types of events.
class CoordinatorLogEventRule(InternalModelWithName):
    """Model matching a coordinator log event type to a rule stating what status(es) must be set
    (not only for the coordinator, but maybe also for group(s), student(s) and teacher(s).
    """

    log_event_type = models.ForeignKey(CoordinatorLogEventType, on_delete=models.CASCADE)
    statuses_to_set = models.JSONField(help_text=JSON_HELP_TEXT)

    class Meta:
        verbose_name_plural = "Rules for status changes after coordinator events"

    def __str__(self):
        return f"Rule for coordinator event '{self.log_event_type}'"


class GroupLogEventRule(InternalModelWithName):
    """Model matching a group log event type to a rule stating what status(es) must be set
    (not only for the group, but maybe also for coordinator(s), student(s) and teacher(s).
    """

    log_event_type = models.ForeignKey(GroupLogEventType, on_delete=models.CASCADE)
    statuses_to_set = models.JSONField(help_text=JSON_HELP_TEXT)

    class Meta:
        verbose_name_plural = "Rules for status changes after group events"

    def __str__(self):
        return f"Rule for group event '{self.log_event_type}'"


class StudentLogEventRule(InternalModelWithName):
    """Model matching a student log event type to a rule stating what status(es) must be set
    (not only for the student, but maybe also for coordinator(s), group(s) and teacher(s).
    """

    log_event_type = models.ForeignKey(StudentLogEventType, on_delete=models.CASCADE)
    statuses_to_set = models.JSONField(help_text=JSON_HELP_TEXT)

    class Meta:
        verbose_name_plural = "Rules for status changes after student events"

    def __str__(self):
        return f"Rule for student event '{self.log_event_type}'"


class TeacherLogEventRule(InternalModelWithName):
    """Model matching a teacher log event type to a rule stating what status(es) must be set
    (not only for the teacher, but maybe also for coordinator(s), group(s) and student(s).
    """

    log_event_type = models.ForeignKey(TeacherLogEventType, on_delete=models.CASCADE)
    statuses_to_set = models.JSONField(help_text=JSON_HELP_TEXT)

    class Meta:
        verbose_name_plural = "Rules for status changes after teacher events"

    def __str__(self):
        return f"Rule for teacher event '{self.log_event_type}'"
