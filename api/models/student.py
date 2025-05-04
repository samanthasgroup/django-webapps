from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from api.models.age_range import AgeRange
from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import StudentProjectStatus, StudentSituationalStatus
from api.models.coordinator import Coordinator
from api.models.day_and_time_slot import DayAndTimeSlot
from api.models.language_and_level import LanguageAndLevel
from api.models.non_teaching_help import NonTeachingHelp
from api.models.shared_abstract.person import Person


class StudentQuerySet(models.QuerySet["Student"]):
    def annotate_with_group_count(self) -> "StudentQuerySet":
        return self.annotate(group_count=Count("groups"))

    def filter_has_groups(self) -> "StudentQuerySet":
        """QuerySet with Students that have at least one group."""
        return self.annotate_with_group_count().filter(group_count__gt=0)

    def filter_has_no_groups(self) -> "StudentQuerySet":
        """QuerySet with Students that have no groups."""
        return self.annotate_with_group_count().filter(group_count=0)


class Student(Person):
    """Model for a student."""

    legacy_sid = models.IntegerField(
        null=True,
        help_text=_("Student id from the old database"),
        verbose_name=_("legacy student id"),
    )
    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text=_(
            "We do not ask students for their exact age. They choose an age range when registering with us."
        ),
        verbose_name=_("age range"),
    )
    availability_slots = models.ManyToManyField(
        DayAndTimeSlot, verbose_name=_("availability slots")
    )
    # irrelevant if student doesn't want to learn English, hence optional
    can_read_in_english = models.BooleanField(
        null=True, blank=True, verbose_name=_("can read in English")
    )
    children = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="parents",
        verbose_name=_("children"),
        help_text=_("children of this student that are also studying at SSG"),
    )
    is_member_of_speaking_club = models.BooleanField(
        default=False,
        verbose_name=_("Speaking club status"),
        help_text=_("Is the student a member of a speaking club at the moment?"),
    )
    non_teaching_help_required = models.ManyToManyField(
        NonTeachingHelp,
        blank=True,
        related_name="students",
        verbose_name=_("Types of non-teaching help this student requires"),
    )

    # JSONField because this will come from external API, so it's good to be protected from changes
    # Just a reminder: the written test is a model with ForeignKey to Student, no field needed here
    smalltalk_test_result = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("SmallTalk test result"),
        help_text=_("JSON received from SmallTalk API"),
    )
    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=StudentProjectStatus.choices,
        verbose_name=_("status in project"),
        help_text=_("status of this student with regard to project as a whole"),
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=StudentSituationalStatus.choices,
        blank=True,
        verbose_name=_("situational status"),
    )

    # The general rule is that one student can only learn one language,
    # but we don't want to limit this in the database.
    teaching_languages_and_levels = models.ManyToManyField(
        LanguageAndLevel, verbose_name=_("teaching languages and levels")
    )
    objects = StudentQuerySet.as_manager()

    alerts = GenericRelation(
        "alerts.Alert",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="student",
    )

    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")
        constraints = [
            models.UniqueConstraint(fields=["legacy_sid"], name="legacy_sid"),
        ]
        indexes = [
            models.Index(fields=("project_status",), name="student_pr_status_idx"),
            models.Index(fields=("situational_status",), name="student_si_status_idx"),
        ]

    @property
    def has_groups(self) -> bool:
        return self.groups.exists()

    @property
    def group_coordinators(self) -> str:
        """Returns names of coordinators associated with student's groups."""
        coordinators = Coordinator.objects.filter(groups__in=self.groups.all()).distinct()
        return ", ".join(coordinator.personal_info.full_name for coordinator in coordinators)
