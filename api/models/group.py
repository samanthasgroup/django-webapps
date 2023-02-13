from django.db import models

from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import TeachingLanguageAndLevel
from api.models.people import Coordinator, Student, Teacher
from api.models.statuses import GroupStatus


# TODO think about group clusters for auto-constructed groups
class Group(models.Model):
    availability_slot = models.ManyToManyField(DayAndTimeSlot)
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.CASCADE)
    lesson_duration = models.IntegerField()
    status = models.ForeignKey(GroupStatus, on_delete=models.PROTECT)
    start_date = models.DateField(blank=True, null=True)
    # this field could be useful for overview, but can be filled automatically when
    # a corresponding log event is created:
    end_date = models.DateField(blank=True, null=True)
    # group chat created manually by the coordinator/teacher
    telegram_chat_url = models.URLField(blank=True, null=True)

    coordinators = models.ManyToManyField(Coordinator)
    students = models.ManyToManyField(Student)
    teachers = models.ManyToManyField(Teacher)

    # some research showed that it's better to store the schedule not in a single text field
    # with some pre-defined syntax, but in 7 columns, one per day of the week
    monday = models.TimeField(blank=True, null=True)
    tuesday = models.TimeField(blank=True, null=True)
    wednesday = models.TimeField(blank=True, null=True)
    thursday = models.TimeField(blank=True, null=True)
    friday = models.TimeField(blank=True, null=True)
    saturday = models.TimeField(blank=True, null=True)
    sunday = models.TimeField(blank=True, null=True)

    def __str__(self):
        coordinator_names = ",".join(c.full_name for c in self.coordinators)
        teacher_names = ",".join(t.full_name for t in self.teachers)
        return (
            f"Group {self.id} (coordinators: {coordinator_names}, teachers: {teacher_names}, "
            f"{len(self.students)} students."
        )
