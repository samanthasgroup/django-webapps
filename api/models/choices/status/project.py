"""Module for 'global' project-level statuses that don't tend to change back and forth."""
from django.db import models

from api.models.auxil.constants import CoordinatorGroupLimit


class CoordinatorProjectStatus(models.TextChoices):
    """Enumeration of possible global statuses of a coordinator."""

    PENDING = "pending", "Completed registration, waiting for onboarding"
    # TODO move to a separate method in model
    WORKING_BELOW_THRESHOLD = (
        "working_threshold_not_reached",
        "Working, but not yet reached the required minimum amount of groups "
        f"({CoordinatorGroupLimit.MIN})",
    )
    WORKING_OK = "working_ok", "Working, required amount of groups reached"
    WORKING_LIMIT_REACHED = (
        "working_limit_reached",
        f"Working, reached maximum number of groups ({CoordinatorGroupLimit.MAX})",
    )
    ON_LEAVE = "on_leave", "On leave"
    LEFT_PREMATURELY = (
        "left_prematurely",
        "Announced that they cannot participate in the project",
    )
    FINISHED_STAYS = "finished_stays", "Finished coordinating but remains in the project"
    FINISHED_LEFT = "finished_left", "Finished coordinating and left the project"
    REMOVED = "removed", "All access revoked, accounts closed"
    BANNED = "banned", "Banned from the project"


class GroupProjectStatus(models.TextChoices):
    """Enumeration of possible statuses of a group."""

    PENDING = "pending", "Pending"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    WORKING = "working", "Working, everything is OK"
    ABORTED = "aborted", "Finished prematurely"
    FINISHED = "finished", "Finished (completed the course)"


class StudentProjectStatus(models.TextChoices):
    """Enumeration of possible statuses of a student."""

    NOT_STUDYING = "not_studying", "Not studying, waiting for a group"
    STUDYING = "study", "Studying in a group"
    ON_LEAVE = "on_leave", "On leave"
    LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
    FINISHED = "finished", "Completed the course and left the project"
    BANNED = "banned", "Banned from the project"


class TeacherProjectStatus(models.TextChoices):
    """Enumeration of possible global statuses of a teacher (young or adult)."""

    NOT_WORKING = "not_working", "Not working, waiting for a group"
    WORKING = "working", "Working"
    # FIXME move to model method:
    TEACHING_ACCEPTING_MORE = "teaching_open", "Teaching, ready to take on another group"
    TEACHING_NOT_ACCEPTING_MORE = "teaching_full", "Teaching, not accepting any more groups"
    ON_LEAVE = "on_leave", "On leave"
    LEFT_PREMATURELY = (
        "left_prematurely",
        "Announced that they cannot participate in the project",
    )
    FINISHED_LEFT = "finished_left", "Finished teaching and left the project"
    FINISHED_STAYS = "finished_stays", "Finished teaching but remains in the project"
    BANNED = "banned", "Banned from the project"
    REMOVED = "removed", "All access revoked, accounts closed"


ProjectStatus = (
    CoordinatorProjectStatus | GroupProjectStatus | StudentProjectStatus | TeacherProjectStatus
)
