from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from api.models.auxil.constants import (
    DEFAULT_CHAR_FIELD_MAX_LEN,
    DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
    CoordinatorGroupLimit,
)
from api.models.choices.status import CoordinatorProjectStatus, CoordinatorSituationalStatus
from api.models.shared_abstract.person import Person


class CoordinatorQuerySet(models.QuerySet["Coordinator"]):
    def annotate_with_group_count(self) -> "CoordinatorQuerySet":
        return self.annotate(group_count=Count("groups"))

    def filter_below_threshold(self) -> "CoordinatorQuerySet":
        """QuerySet with coordinators with not enough groups."""
        return self.annotate_with_group_count().filter(group_count__lt=CoordinatorGroupLimit.MIN)

    def filter_above_threshold_and_within_limit(self) -> "CoordinatorQuerySet":
        """QuerySet with coordinators that are above threshold and within limit."""
        return self.annotate_with_group_count().filter(
            group_count__gte=CoordinatorGroupLimit.MIN,
            group_count__lt=CoordinatorGroupLimit.MAX,
        )

    def filter_limit_reached(self) -> "CoordinatorQuerySet":
        """QuerySet with coordinators that have exceeded the limit of groups."""
        return self.annotate_with_group_count().filter(group_count__gte=CoordinatorGroupLimit.MAX)

    def filter_active(self) -> "CoordinatorQuerySet":
        """QuerySet with Coordinators that are active."""
        return self.filter(project_status__in=CoordinatorProjectStatus.active_statuses())


class Coordinator(Person):
    """Model for a coordinator."""

    legacy_cid = models.IntegerField(null=True, help_text="Coordinator id from the old database")
    additional_skills_comment = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN,  # prefer this to TextField for a better search
        blank=True,
        verbose_name=_("comment on additional skills"),
    )
    is_admin = models.BooleanField(
        default=False,
        help_text=_(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
    is_validated = models.BooleanField(
        help_text=_("Has an initial validation interview been conducted with this teacher?")
    )
    mentor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interns",
        help_text=_("mentor of this coordinator. One coordinator can have many interns"),
    )
    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CoordinatorProjectStatus.choices,
        verbose_name=_("status in project"),
        help_text=_("status of this coordinator with regard to project as a whole"),
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CoordinatorSituationalStatus.choices,
        blank=True,
    )
    role_comment = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN,
        blank=True,
        help_text=_("phrase describing the role of coordinator in project"),
    )

    objects = CoordinatorQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["legacy_cid"], name="legacy_cid"),
        ]
        indexes = [
            models.Index(fields=("project_status",), name="coordinator_pr_status_idx"),
            models.Index(fields=("situational_status",), name="coordinator_si_status_idx"),
        ]

    @property
    def has_enough_groups(self) -> bool:
        """Returns `True` if coordinator has required minimum amount of groups."""
        return self.groups.count() >= CoordinatorGroupLimit.MIN

    @property
    def has_reached_group_limit(self) -> bool:
        """Returns `True` if coordinator has reached maximum amount of groups."""
        return self.groups.count() >= CoordinatorGroupLimit.MAX
