from django.db import models
from django.db.models import Count

from api.models.age_range import AgeRange
from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import TeacherProjectStatus, TeacherSituationalStatus
from api.models.day_and_time_slot import DayAndTimeSlot
from api.models.non_teaching_help import NonTeachingHelp
from api.models.shared_abstract.teacher_common import TeacherCommon


class TeacherQuerySet(models.QuerySet["Teacher"]):
    def annotate_with_group_count(self) -> "TeacherQuerySet":
        return self.annotate(group_count=Count("groups"))

    def filter_has_groups(self) -> "TeacherQuerySet":
        """QuerySet with Teachers that have at least one group."""
        return self.annotate_with_group_count().filter(group_count__gt=0)

    def filter_has_no_groups(self) -> "TeacherQuerySet":
        """QuerySet with Teachers that have no groups."""
        return self.annotate_with_group_count().filter(group_count=0)


class Teacher(TeacherCommon):
    """Model for an adult teacher that can teach groups."""

    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    has_prior_teaching_experience = models.BooleanField(
        default=False,
        help_text="has the applicant already worked as a teacher before applying at Samantha "
        "Smith's Group?",
    )
    non_teaching_help_provided = models.ManyToManyField(
        NonTeachingHelp,
        blank=True,
        related_name="teachers",
        verbose_name="Types of non-teaching help this teacher can provide to students",
    )

    # Peer support. When a new teacher is added, they cannot have these set to True unless they
    # have prior teaching experience.  However, the `.has_prior_teaching_experience` is meant
    # to stay unchanged (it describes experience before coming to Samantha Smith's Group),
    # while it's imaginable that if a teacher teaches long enough, they will be allowed to consult
    # other teachers.  So these flags being here doesn't really break the 3rd normal form.
    peer_support_can_check_syllabus = models.BooleanField(
        default=False, verbose_name="peer support: can check syllabus"
    )
    peer_support_can_host_mentoring_sessions = models.BooleanField(
        default=False, verbose_name="peer support: can host individual or group mentoring sessions"
    )
    peer_support_can_give_feedback = models.BooleanField(
        default=False, verbose_name="peer support: can give feedback"
    )
    peer_support_can_help_with_childrens_groups = models.BooleanField(
        default=False,
        verbose_name="peer support: can help with children's groups",
    )
    peer_support_can_provide_materials = models.BooleanField(
        default=False, verbose_name="peer support: can provide teaching materials"
    )
    peer_support_can_invite_to_class = models.BooleanField(
        default=False,
        verbose_name="peer support: can invite other teachers to their class",
    )
    peer_support_can_work_in_tandem = models.BooleanField(
        default=False,
        verbose_name="peer support: can work in tandem with a less experienced teacher",
    )

    simultaneous_groups = models.PositiveSmallIntegerField(
        default=1, help_text="number of groups the teacher can teach simultaneously"
    )
    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherProjectStatus.choices,
        verbose_name="status in project",
        help_text="status of this student with regard to project as a whole",
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherSituationalStatus.choices,
        blank=True,
    )
    student_age_ranges = models.ManyToManyField(
        AgeRange,
        help_text="age ranges of students that the teacher is willing to teach. "
        "The 'from's and 'to's of these ranges are wider than those the students choose "
        "for themselves.",
    )
    weekly_frequency_per_group = models.PositiveSmallIntegerField(
        help_text=(
            "number of times per week the teacher can have classes with each group. "
            "This column will be ignored if the teacher currently doesn't want to teach any "
            "groups (in which case the column 'simultaneous groups' will have value 0). The "
            "value of frequency column does NOT have to be 0 in this case. Maybe the teacher will "
            "start (or return to) group studies and the frequency column will become relevant."
        )
    )

    objects = TeacherQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=("project_status",), name="teacher_project_status_idx"),
            models.Index(fields=("situational_status",), name="teacher_situational_status_idx"),
        ]

    @property
    def can_take_more_groups(self) -> bool:
        """`True` if a teacher can take more groups than they already have."""
        return self.groups.count() < self.simultaneous_groups
