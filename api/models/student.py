from django.db import models
from django.db.models import Count

from api.models.age_range import AgeRange
from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import StudentProjectStatus, StudentSituationalStatus
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

    legacy_sid = models.IntegerField(null=True, help_text="Student id from the old database")
    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text="We do not ask students for their exact age. "
        "They choose an age range when registering with us.",
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)
    # irrelevant if student doesn't want to learn English, hence optional
    can_read_in_english = models.BooleanField(null=True, blank=True)
    children = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="parents",
        help_text="children of this student that are also studying at SSG",
    )
    is_member_of_speaking_club = models.BooleanField(
        default=False,
        verbose_name="Speaking club status",
        help_text="Is the student a member of a speaking club at the moment?",
    )
    non_teaching_help_required = models.ManyToManyField(
        NonTeachingHelp,
        blank=True,
        related_name="students",
        verbose_name="Types of non-teaching help this student requires",
    )

    # JSONField because this will come from external API, so it's good to be protected from changes
    # Just a reminder: the written test is a model with ForeignKey to Student, no field needed here
    smalltalk_test_result = models.JSONField(
        null=True, blank=True, help_text="JSON received from SmallTalk API"
    )

    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=StudentProjectStatus.choices,
        verbose_name="status in project",
        help_text="status of this student with regard to project as a whole",
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=StudentSituationalStatus.choices,
        blank=True,
    )

    # The general rule is that one student can only learn one language,
    # but we don't want to limit this in the database.
    teaching_languages_and_levels = models.ManyToManyField(LanguageAndLevel)
    objects = StudentQuerySet.as_manager()

    class Meta:
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
