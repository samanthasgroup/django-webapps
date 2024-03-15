from django.db import models
from django.db.models import Count, Q, QuerySet

from api.models.auxil.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.choices.status import GroupProjectStatus, GroupSituationalStatus
from api.models.coordinator import Coordinator
from api.models.day_and_time_slot import DayAndTimeSlot
from api.models.language_and_level import Language, LanguageAndLevel
from api.models.shared_abstract.group_or_person import GroupOrPerson
from api.models.student import Student
from api.models.teacher import Teacher
from api.models.teacher_under_18 import TeacherUnder18


class GroupCommon(GroupOrPerson):
    """Abstract model for attributes shared by regular groups and speaking clubs."""

    # %(class)ss will produce "groups" for Group and "speakingclubs" for SpeakingClub
    coordinators = models.ManyToManyField(Coordinator, related_name="%(class)ss")
    students = models.ManyToManyField(Student, related_name="%(class)ss")
    teachers = models.ManyToManyField(Teacher, related_name="%(class)ss")
    comment = models.TextField(blank=True)
    coordinators_former = models.ManyToManyField(
        Coordinator,
        blank=True,
        related_name="%(class)ss_former",
        verbose_name="Former coordinators",
        help_text=(
            "Lists coordinators that once worked with this group and/or the coordinator(s) of "
            "this group when it finished classes or was aborted."
        ),
    )
    students_former = models.ManyToManyField(
        Student,
        blank=True,
        related_name="%(class)ss_former",
        verbose_name="Former students",
        help_text=(
            "Lists students that once worked with this group and/or all students of this group "
            "when it finished classes or was aborted."
        ),
    )
    teachers_former = models.ManyToManyField(
        Teacher,
        blank=True,
        related_name="%(class)ss_former",
        verbose_name="Former teachers",
        help_text=(
            "Lists teachers that once worked with this group, and/or the teacher(s) of this group "
            "when it finished classes or was aborted."
        ),
    )

    # group chat created manually by the coordinator/teacher
    # null=True due to unqiue constraint and we can not use empty string in this case
    telegram_chat_url = models.URLField(blank=True, null=True)  # noqa: DJ001

    class Meta:
        abstract = True


# TODO think about group clusters for auto-constructed groups
class Group(GroupCommon):
    """Model for a regular language group."""

    availability_slots_for_auto_matching = models.ManyToManyField(DayAndTimeSlot)
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(LanguageAndLevel, on_delete=models.PROTECT)
    lesson_duration_in_minutes = models.PositiveSmallIntegerField()
    project_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=GroupProjectStatus.choices
    )
    situational_status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=GroupSituationalStatus.choices,
        blank=True,
    )
    status_since = models.DateTimeField(
        help_text="date and time of last change of project-level or situational status"
    )
    start_date = models.DateField(null=True, blank=True)
    # this field could be useful for overview, but can be filled automatically when
    # a corresponding log event is created:
    end_date = models.DateField(null=True, blank=True)

    # some research showed that it's better to store the schedule not in a single text field
    # with some pre-defined syntax, but in 7 columns, one per day of the week
    monday = models.TimeField(null=True, blank=True)
    tuesday = models.TimeField(null=True, blank=True)
    wednesday = models.TimeField(null=True, blank=True)
    thursday = models.TimeField(null=True, blank=True)
    friday = models.TimeField(null=True, blank=True)
    saturday = models.TimeField(null=True, blank=True)
    sunday = models.TimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["telegram_chat_url"], name="telegram_chat_url"),
            models.CheckConstraint(
                check=Q(monday__isnull=False)
                | Q(tuesday__isnull=False)
                | Q(wednesday__isnull=False)
                | Q(thursday__isnull=False)
                | Q(friday__isnull=False)
                | Q(saturday__isnull=False)
                | Q(sunday__isnull=False),
                name="at_least_one_day_time_slot_must_be_selected",
            ),
        ]
        indexes = [
            models.Index(fields=("language_and_level",), name="group_language_level_idx"),
            models.Index(fields=("project_status",), name="group_pr_status_idx"),
            models.Index(fields=("situational_status",), name="group_si_status_idx"),
            models.Index(fields=("start_date",), name="group_start_date_idx"),
        ]

    def __str__(self) -> str:
        coordinator_names = ",".join(c.personal_info.full_name for c in self.coordinators.all())
        teacher_names = ",".join(t.personal_info.full_name for t in self.teachers.all())
        return (
            f"Group {self.pk}, {self.language_and_level} (coordinators: {coordinator_names}, "
            f"teachers: {teacher_names}, {self.students.count()} students.)"
        )

    def _teachers_group_count_annotation(self) -> QuerySet[Teacher]:
        return self.teachers.annotate(group_count=Count("groups"))

    def teachers_with_other_groups(self) -> QuerySet[Teacher]:
        return self._teachers_group_count_annotation().filter(group_count__gt=1)

    def teachers_with_no_other_groups(self) -> QuerySet[Teacher]:
        return self._teachers_group_count_annotation().filter(group_count__lte=1)


class SpeakingClub(GroupCommon):
    """Model for a speaking club (a group without any changing status or fixed schedule)."""

    is_for_children = models.BooleanField(
        verbose_name="Is this a speaking club for children?", default=False
    )
    # a speaking club has no fixed level, so putting language only
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    # in addition to regular teachers, a speaking club can have young teachers
    teachers_under_18 = models.ManyToManyField(TeacherUnder18)

    def __str__(self) -> str:
        category = "children" if self.is_for_children else "adults"
        return f"{self.language} speaking club for {category}, {self.students.count()} students."
