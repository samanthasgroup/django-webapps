from django.db import models
from django.db.models import Q

from api.models.base import GroupOrPerson
from api.models.choices.statuses import GroupStatus
from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH
from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import Language, LanguageAndLevel
from api.models.people import Coordinator, Student, Teacher, TeacherUnder18


class GroupCommon(GroupOrPerson):
    """Abstract model for attributes shared by regular groups and speaking clubs."""

    # %(class)ss will produce "groups" for Group and "speakingclubs" for SpeakingClub
    coordinators = models.ManyToManyField(Coordinator, related_name="%(class)ss")
    students = models.ManyToManyField(Student, related_name="%(class)ss")
    teachers = models.ManyToManyField(Teacher, related_name="%(class)ss")
    # group chat created manually by the coordinator/teacher
    telegram_chat_url = models.URLField(blank=True)

    class Meta:
        abstract = True


# TODO think about group clusters for auto-constructed groups
class Group(GroupCommon):
    """Model for a regular language group."""

    availability_slots_for_auto_matching = models.ManyToManyField(DayAndTimeSlot)
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(LanguageAndLevel, on_delete=models.PROTECT)
    lesson_duration_in_minutes = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=GroupStatus.choices
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
            models.Index(fields=("status",), name="group_status_idx"),
            models.Index(fields=("start_date",), name="group_start_date_idx"),
        ]

    def __str__(self) -> str:
        coordinator_names = ",".join(c.personal_info.full_name for c in self.coordinators.all())
        teacher_names = ",".join(t.personal_info.full_name for t in self.teachers.all())
        return (
            f"Group {self.pk}, {self.language_and_level} (coordinators: {coordinator_names}, "
            f"teachers: {teacher_names}, {self.students.count()} students."
        )


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
