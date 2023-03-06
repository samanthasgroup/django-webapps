from django.db import models

from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import (
    CommunicationLanguageMode,
    TeachingLanguage,
    TeachingLanguageAndLevel,
)
from api.models.people import Coordinator, Student, Teacher
from api.models.statuses import GroupStatus


class GroupCommon(models.Model):
    """Abstract model for attributes shared by regular groups and speaking clubs."""

    coordinators = models.ManyToManyField(Coordinator)
    students = models.ManyToManyField(Student)
    teachers = models.ManyToManyField(Teacher)
    # group chat created manually by the coordinator/teacher
    telegram_chat_url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True


# TODO think about group clusters for auto-constructed groups
class Group(GroupCommon):
    """Model for a regular language group."""

    availability_slot = models.ManyToManyField(DayAndTimeSlot)
    communication_language_mode = models.ForeignKey(
        CommunicationLanguageMode, on_delete=models.PROTECT
    )
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.PROTECT)
    lesson_duration = models.PositiveSmallIntegerField()
    status = models.ForeignKey(GroupStatus, on_delete=models.PROTECT)
    status_since = models.DateTimeField(auto_now=True)
    start_date = models.DateField(blank=True, null=True)
    # this field could be useful for overview, but can be filled automatically when
    # a corresponding log event is created:
    end_date = models.DateField(blank=True, null=True)

    # some research showed that it's better to store the schedule not in a single text field
    # with some pre-defined syntax, but in 7 columns, one per day of the week
    monday = models.TimeField(blank=True, null=True)
    tuesday = models.TimeField(blank=True, null=True)
    wednesday = models.TimeField(blank=True, null=True)
    thursday = models.TimeField(blank=True, null=True)
    friday = models.TimeField(blank=True, null=True)
    saturday = models.TimeField(blank=True, null=True)
    sunday = models.TimeField(blank=True, null=True)

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

    def __str__(self):
        category = "children" if self.is_for_children else "adults"
        return f"{self.language} speaking club for {category}, {self.students.count()} students."
