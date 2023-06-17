from django.db import models

from api.models.auxil.constants import STUDENT_CLASS_MISS_LIMIT, CoordinatorGroupLimit


class CoordinatorStatus(models.TextChoices):
    """Enumeration of possible statuses of a coordinator."""

    PENDING = "pending", "Completed registration, waiting for onboarding"
    ONBOARDING = "onboarding", "In onboarding"
    ONBOARDING_STALE = (
        "onboarding_stale",
        "Has been in onboarding for too long without taking a group",
    )
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
    NO_RESPONSE = "no_response", "Not responding"
    LEFT_PREMATURELY = (
        "left_prematurely",
        "Announced that they cannot participate in the project",
    )
    FINISHED_STAYS = "finished_stays", "Finished coordinating but remains in the project"
    FINISHED_LEFT = "finished_left", "Finished coordinating and left the project"
    REMOVED = "removed", "All access revoked, accounts closed"
    BANNED = "banned", "Banned from the project"


class GroupStatus(models.TextChoices):
    """Enumeration of possible statuses of a group."""

    PENDING = "pending", "Pending"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    WORKING = "working", "Working, everything is OK"
    ATTENTION_REQUIRED = (
        "attention",
        "Some sort of problem: needs substitute teacher, change of coordinator etc.",
    )
    ABORTED = "aborted", "Finished prematurely"
    FINISHED = "finished", "Finished (completed the course)"


class StudentStatus(models.TextChoices):
    """Enumeration of possible statuses of a student."""

    AWAITING_OFFER = "awaiting_offer", "Registration complete, waiting for a group"
    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    STUDYING = "study", "Studying in a group"
    NOT_ATTENDING = (
        "not_attending",
        f"Missed {STUDENT_CLASS_MISS_LIMIT} classes in a row without letting the teacher know",
    )
    NEEDS_TRANSFER = "needs_transfer", "Needs transfer to another group"
    NO_RESPONSE = "no_response", "Not responding"
    LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
    FINISHED = "finished", "Completed the course and left the project"
    BANNED = "banned", "Banned from the project"


class TeacherStatus(models.TextChoices):
    """Enumeration of possible statuses of an adult teacher."""

    AWAITING_OFFER = "awaiting_offer", "Registered and waiting for a group"
    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    TEACHING_ACCEPTING_MORE = "teaching_open", "Teaching, ready to take on another group"
    TEACHING_NOT_ACCEPTING_MORE = "teaching_full", "Teaching, not accepting any more groups"
    TEACHING_ANOTHER_GROUP_OFFERED = (
        "teaching_another_offered",
        "Teaching, received offer for another group",
    )
    TEACHING_AWAITING_START_OF_ANOTHER = (
        "teaching_another_awaiting_start",
        "Teaching, awaiting start of another group",
    )
    NEEDS_SUBSTITUTION = (
        "needs_substitution",
        "Needs a break in teaching the group, substitute teacher needed",
    )
    ON_LEAVE = "on_leave", "On leave"
    NO_RESPONSE = "no_response", "Not responding"
    LEFT_PREMATURELY = (
        "left_prematurely",
        "Announced that they cannot participate in the project",
    )
    FINISHED_LEFT = "finished_left", "Finished teaching and left the project"
    FINISHED_STAYS = "finished_stays", "Finished teaching but remains in the project"
    BANNED = "banned", "Banned from the project"
    REMOVED = "removed", "All access revoked, accounts closed"


class TeacherUnder18Status(models.TextChoices):
    """Enumeration of possible statuses of a teacher under 18 years old."""

    ACTIVE = "active", "Completed registration in the bot"
    ON_LEAVE = "on_leave", "On leave"
    NO_RESPONSE = "no_response", "Not responding"
    LEFT_PREMATURELY = (
        "left_prematurely",
        "Announced that they cannot participate in the project",
    )
    FINISHED_LEFT = "finished_left", "Finished teaching and left the project"
    FINISHED_STAYS = "finished_stays", "Finished teaching but remains in the project"
    BANNED = "banned", "Banned from the project"
    REMOVED = "removed", "All access revoked, accounts closed"


Status = CoordinatorStatus | GroupStatus | StudentStatus | TeacherStatus | TeacherUnder18Status
