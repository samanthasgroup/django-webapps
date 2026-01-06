"""Module for project-level statuses that describe the 'main state' of a person or a group."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import CoordinatorGroupLimit


class CoordinatorProjectStatus(models.TextChoices):
    """Enumeration of possible project-level statuses of a coordinator."""

    PENDING = "pending", _("Completed registration, but not in working status yet")
    WORKING_BELOW_THRESHOLD = (
        "working_below_threshold",
        _("Working, but not yet reached the required minimum amount of groups (%(min)d)")
        % {"min": CoordinatorGroupLimit.MIN},
    )
    WORKING_OK = "working_ok", _("Working, required amount of groups reached")
    WORKING_LIMIT_REACHED = (
        "working_limit_reached",
        _("Working, reached maximum number of groups (%(max)d)") % {"max": CoordinatorGroupLimit.MAX},
    )
    ON_LEAVE = "on_leave", _("On leave")
    LEFT_PREMATURELY = "left_prematurely", _("Announced that they cannot participate in the project")
    FINISHED_STAYS = "finished_stays", _("Finished coordinating but remains in the project")
    FINISHED_LEFT = "finished_left", _("Finished coordinating and left the project")
    REMOVED = "removed", _("All access revoked, accounts closed")
    BANNED = "banned", _("Banned from the project")

    @classmethod
    def active_statuses(cls) -> list["CoordinatorProjectStatus"]:
        return [
            cls.WORKING_BELOW_THRESHOLD,
            cls.WORKING_OK,
            cls.WORKING_LIMIT_REACHED,
        ]


class GroupProjectStatus(models.TextChoices):
    """Enumeration of possible project-level statuses of a group."""

    PENDING = "pending", _("Pending")
    AWAITING_START = "awaiting_start", _("Group confirmed, awaiting start of classes")
    WORKING = "working", _("Working, everything is OK")
    ABORTED = "aborted", _("Finished prematurely")
    FINISHED = "finished", _("Finished (completed the course)")


class StudentProjectStatus(models.TextChoices):
    """Enumeration of possible project-level statuses of a student."""

    NEEDS_INTERVIEW_TO_DETERMINE_LEVEL = (
        "needs_interview_to_determine_level",
        _("Requires oral interview to determine language levelbefore getting 'no_group_yet' status"),
    )
    NO_GROUP_YET = "no_group_yet", _("Not studying, waiting for a group")
    STUDYING = "study", _("Studying in a group")
    ON_LEAVE = "on_leave", _("On leave")
    LEFT_PREMATURELY = "left_prematurely", _("Left the project prematurely")
    FINISHED = "finished", _("Completed the course and left the project")
    BANNED = "banned", _("Banned from the project")


class TeacherProjectStatus(models.TextChoices):
    """Enumeration of possible project-level statuses of a teacher (young or adult)."""

    NO_GROUP_YET = "no_group_yet", _("Not working, waiting for a group")
    WORKING = "working", _("Working")
    ON_LEAVE = "on_leave", _("On leave")
    LEFT_PREMATURELY = (
        "left_prematurely",
        _("Announced that they cannot participate in the project"),
    )
    FINISHED_LEFT = "finished_left", _("Finished teaching and left the project")
    FINISHED_STAYS = "finished_stays", _("Finished teaching but remains in the project")
    BANNED = "banned", _("Banned from the project")
    REMOVED = "removed", _("All access revoked, accounts closed")

    @classmethod
    def active_statuses(cls) -> list["TeacherProjectStatus"]:
        return [
            cls.NO_GROUP_YET,
            cls.WORKING,
        ]


ProjectStatus = CoordinatorProjectStatus | GroupProjectStatus | StudentProjectStatus | TeacherProjectStatus
