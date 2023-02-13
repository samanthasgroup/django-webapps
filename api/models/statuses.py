from django.db import models

from api.models.aux import InternalModelWithName


# We could have created one table listing all possible status names, but that might look confusing
# for admin users later on.  It seems more convenient for them to have separate tables.
class CoordinatorStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a coordinator."""


class GroupStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a group."""


class StudentStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a student."""


class TeacherStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a teacher."""


class Status(models.Model):
    """Abstract model for an actual status of a group or person. Combines a status name
    (selected from allowed status names) with a time that indicates when this status was assigned.
    """

    # this can be tracked via LogEvents but an additional column can be a convenient shortcut:
    in_place_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CoordinatorStatus(Status):
    """Model for statuses of coordinators."""

    name = models.ForeignKey(CoordinatorStatusName, on_delete=models.CASCADE)


class GroupStatus(Status):
    """Model for statuses of groups."""

    name = models.ForeignKey(GroupStatusName, on_delete=models.CASCADE)


class StudentStatus(Status):
    """Model for statuses of students."""

    name = models.ForeignKey(StudentStatusName, on_delete=models.CASCADE)


class TeacherStatus(Status):
    """Model for statuses of teachers."""

    name = models.ForeignKey(TeacherStatusName, on_delete=models.CASCADE)
