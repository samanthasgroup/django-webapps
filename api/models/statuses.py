from api.models.base import InternalModelWithName


# We could have created one table listing all possible status names, but that might look confusing
# for admin users later on.  It seems more convenient for them to have separate tables.
class CoordinatorStatus(InternalModelWithName):
    """Model for enumeration of possible statuses of a coordinator."""

    class Meta:
        verbose_name_plural = "possible coordinator statuses"


class GroupStatus(InternalModelWithName):
    """Model for enumeration of possible statuses of a group."""

    class Meta:
        verbose_name_plural = "possible group statuses"


class StudentStatus(InternalModelWithName):
    """Model for enumeration of possible statuses of a student with regard to group studies."""

    class Meta:
        verbose_name_plural = "possible student statuses (group studies)"


class TeacherStatus(InternalModelWithName):
    """Model for enumeration of possible statuses of a teacher with regard to group studies."""

    class Meta:
        verbose_name_plural = "possible teacher statuses (group studies)"
