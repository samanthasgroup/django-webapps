from django.db import models

from api.models.constants import STATUS_MAX_LEN
from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import (
    CommunicationLanguageMode,
    TeachingLanguage,
    TeachingLanguageAndLevel,
)
from api.models.people import Coordinator, Student, Teacher, TeacherUnder18


class GroupCommon(models.Model):
    """Abstract model for attributes shared by regular groups and speaking clubs."""

    coordinators = models.ManyToManyField(Coordinator)
    students = models.ManyToManyField(Student)
    teachers = models.ManyToManyField(Teacher)
    # group chat created manually by the coordinator/teacher
    telegram_chat_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True


# TODO think about group clusters for auto-constructed groups
class Group(GroupCommon):
    """Model for a regular language group."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        STUDYING = "study", "Studying"
        FINISHED = "finish", "Finished"
        # TODO put statuses here once they are finalized

    availability_slot = models.ManyToManyField(DayAndTimeSlot)
    communication_language_mode = models.ForeignKey(
        CommunicationLanguageMode, on_delete=models.PROTECT
    )
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.PROTECT)
    lesson_duration = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=STATUS_MAX_LEN, choices=Status.choices)
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
            models.UniqueConstraint(fields=["telegram_chat_url"], name="telegram_chat_url")
        ]

    def __str__(self):
        coordinator_names = ",".join(c.full_name for c in self.coordinators.all())
        teacher_names = ",".join(t.full_name for t in self.teachers.all())
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
    language = models.ForeignKey(TeachingLanguage, on_delete=models.PROTECT)
    # in addition to regular teachers, a speaking club can have young teachers
    teachers_under_18 = models.ManyToManyField(TeacherUnder18)

    def __str__(self):
        category = "children" if self.is_for_children else "adults"
        return f"{self.language} speaking club for {category}, {self.students.count()} students."
