"""Module for temporary statuses that can 'turn on and off' again depending on situation."""

import typing

from django.db import models

from api.models.auxil.constants import STUDENT_CLASS_MISS_LIMIT


class CoordinatorSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a coordinator."""

    ONBOARDING = "onboarding", "In onboarding"
    STALE = (
        "onboarding_stale",
        "Has been in onboarding for too long without taking a group",
    )
    NO_RESPONSE = "no_response", "Not responding"


class GroupSituationalStatus(models.TextChoices):
    """Enumeration of possible statuses of a group."""

    ATTENTION_REQUIRED = (
        "attention",
        "Some sort of problem: needs substitute teacher, change of coordinator etc.",
    )


class StudentSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a student."""

    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    NOT_ATTENDING = (
        "not_attending",
        f"Missed {STUDENT_CLASS_MISS_LIMIT} classes in a row without letting the teacher know",
    )
    NEEDS_TRANSFER = "needs_transfer", "Needs transfer to another group"
    NO_RESPONSE = "no_response", "Not responding"


class TeacherSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a young or adult teacher."""

    # Young teachers may not need all of these, but it doesn't make any sense
    # to create a separate class
    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
    NEEDS_SUBSTITUTION = (
        "needs_substitution",
        "Needs a break in teaching the group, substitute teacher needed",
    )
    NO_RESPONSE = "no_response", "Not responding"


SituationalStatus = (
    CoordinatorSituationalStatus
    | GroupSituationalStatus
    | StudentSituationalStatus
    | TeacherSituationalStatus
    | typing.Literal[""]
)

CoordinatorSituationalStatusOrEmpty = CoordinatorSituationalStatus | typing.Literal[""]
