"""Module for temporary statuses that can 'turn on and off' again depending on situation."""

import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import STUDENT_CLASS_MISS_LIMIT


class CoordinatorSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a coordinator."""

    STALE = (
        "onboarding_stale",
        _("Has been in onboarding for too long without taking a group"),
    )
    NO_RESPONSE = "no_response", _("Not responding")


class GroupSituationalStatus(models.TextChoices):
    """Enumeration of possible statuses of a group."""

    ATTENTION_REQUIRED = (
        "attention",
        _("Some sort of problem: needs substitute teacher, change of coordinator etc."),
    )
    HOLIDAY = ("holiday", _("Holiday"))


class StudentSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a student."""

    GROUP_OFFERED = "group_offered", _("Was offered a group, has not responded yet")
    AWAITING_START = "awaiting_start", _("Group confirmed, awaiting start of classes")
    NOT_ATTENDING = (
        "not_attending",
        _("Missed {miss_limit} classes in a row without letting the teacher know").format(
            miss_limit=STUDENT_CLASS_MISS_LIMIT
        ),
    )
    NEEDS_TRANSFER = "needs_transfer", _("Needs transfer to another group")
    NO_RESPONSE = "no_response", _("Not responding")


class TeacherSituationalStatus(models.TextChoices):
    """Enumeration of possible transient statuses of a young or adult teacher."""

    GROUP_OFFERED = "group_offered", _("Was offered a group, has not responded yet")
    AWAITING_START = "awaiting_start", _("Group confirmed, awaiting start of classes")
    NEEDS_SUBSTITUTION = (
        "needs_substitution",
        _("Needs a break in teaching the group, substitute teacher needed"),
    )
    NO_RESPONSE = "no_response", _("Not responding")


SituationalStatus = (
    CoordinatorSituationalStatus
    | GroupSituationalStatus
    | StudentSituationalStatus
    | TeacherSituationalStatus
    | typing.Literal[""]
)

CoordinatorSituationalStatusOrEmpty = CoordinatorSituationalStatus | typing.Literal[""]
