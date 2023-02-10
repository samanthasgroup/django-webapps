import uuid

from django.db import models


class MultilingualObject(models.Model):
    class Meta:
        abstract = True  # This model will not be used to create any database table

    name_en = models.CharField
    name_ru = models.CharField
    name_ua = models.CharField


class AdminSiteUser(models.Model):
    login = models.CharField(max_length=70)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


# LANGUAGES AND LEVELS
class TeachingLanguage(MultilingualObject):
    ...


class LanguageLevel(models.Model):
    name = models.CharField(max_length=3)
    rank = models.IntegerField


class TeachingLanguageAndLevel(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)


# DAYS OF WEEK AND TIME SLOTS
class DayOfWeek(MultilingualObject):
    # We could just use numbers and then localize them using Babel,
    # but it seems easier to just create a table with 7 rows.
    index = models.IntegerField  # for sorting


class TimeSlot(models.Model):
    from_utc_hour = models.IntegerField
    to_utc_hour = models.IntegerField


class DayAndTimeSlot(models.Model):
    day_of_week = models.ForeignKey(DayOfWeek, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)


# STATUSES
class Status(models.Model):
    name = models.CharField
    # this can be tracked via LogItems but an additional column can be a very convenient shortcut:
    in_place_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CoordinatorStatus(Status):
    """Model for statuses of coordinators."""


class GroupStatus(Status):
    """Model for statuses of groups."""


class StudentStatus(Status):
    """Model for statuses of students."""


class TeacherStatus(Status):
    """Model for statuses of teachers."""


# BLOCKS WITH ADDITIONAL INFORMATION ON A PERSON WITH A SPECIFIC ROLE
class CoordinatorInfo(models.Model):
    """Additional information about a coordinator. If an instance of Person has this attribute,
    this person is a coordinator.
    """

    is_admin = models.BooleanField(default=False)
    status = models.ForeignKey(CoordinatorStatus, on_delete=models.PROTECT)


class StudentInfo(models.Model):
    """Additional information about a student. If an instance of Person has this attribute, this
    person is a student.
    """

    is_member_of_speaking_club = models.BooleanField
    requires_help_with_CV = models.BooleanField
    requires_communication_in_ukrainian = models.BooleanField
    status = models.ForeignKey(StudentStatus, on_delete=models.PROTECT)
    # The general rule is that one student can only learn one language,
    # but we don't want to limit this in the database.
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)


class TeacherInfo(models.Model):
    """Additional information about a teacher. If an instance of Person has this attribute, this
    person is a teacher.
    """

    status = models.ForeignKey(TeacherStatus, on_delete=models.PROTECT)
    # teacher_categories = models.ManyToManyField  # TODO
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)


# LOG ITEMS
class LogItem(models.Model):
    """Abstract class for some sort of internal event ('log item'), e.g. 'joined group' for a
    student or 'finished' for a group. Statuses will be assigned based on these events.

    We don't call the class Event (although it is an event in a programming sense) for it not to be
    confused with possible models for events organized by the school.
    """

    date_time = models.DateTimeField(auto_now_add=True)
    type = models.CharField  # TODO add accepted events to another table or just create an Enum?

    class Meta:
        abstract = True


class GroupLogItem(LogItem):
    group = models.ForeignKey("Group", on_delete=models.CASCADE)


class PersonLogItem(LogItem):
    """Abstract class for log items for coordinators, students and teachers."""

    from_group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="log_from_self")
    to_group = models.ForeignKey("Group", on_delete=models.CASCADE, related_name="log_to_self")

    class Meta:
        abstract = True


class CoordinatorLogItem(PersonLogItem):
    coordinator = models.ForeignKey(CoordinatorInfo, related_name="log", on_delete=models.CASCADE)


class StudentLogItem(PersonLogItem):
    student = models.ForeignKey(StudentInfo, related_name="log", on_delete=models.CASCADE)


class TeacherLogItem(PersonLogItem):
    teacher = models.ForeignKey(TeacherInfo, related_name="log", on_delete=models.CASCADE)


# PEOPLE AND GROUPS
class Person(models.Model):
    """Model for a coordinator, student, or teacher. We are not using an abstract model here
    because people can combine roles (be a teacher and a coordinator at the same time),
    and it makes sense to put them in one table.
    """

    # This is the ID that will identify a person with any role (student, teacher, coordinator),
    # even if one person combines several roles.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Automatically save date and time when the Person was created.
    date_and_time_added = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)  # can include middle name if a person wishes so
    last_name = models.CharField(max_length=100)
    tg_username = models.CharField
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    tz_summer_relative_to_utc = models.IntegerField
    tz_winter_relative_to_utc = models.IntegerField
    approximate_date_of_birth = models.DateField

    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    # these are none for coordinator, but can be present for student/teacher, so keeping them here
    registration_bot_chat_id = models.IntegerField(blank=True, null=True)
    chatwoot_conversation_id = models.IntegerField(blank=True, null=True)

    # native_language = models.ForeignKey  # TODO
    # source  # TODO: how they learned about SSG, this could be an Enum

    # blank = True and null = True mean that this attribute is optional.
    # The logic is that if a person has coordinator_info, they are a coordinator, etc.
    coordinator_info = models.OneToOneField(
        "CoordinatorInfo",
        on_delete=models.CASCADE,  # TODO check if this is correct for OneToOneField
        blank=True,
        null=True,
    )
    student_info = models.OneToOneField(
        "StudentInfo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    teacher_info = models.OneToOneField(
        "TeacherInfo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        # TODO display whether it's a teacher, a student, a coordinator, or a combination of these
        return f"{self.first_name} {self.last_name}"


class Group(models.Model):
    availability_slot = models.ManyToManyField(DayAndTimeSlot)
    is_for_staff_only = models.BooleanField(default=False)
    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.CASCADE)
    status = models.ForeignKey(GroupStatus, on_delete=models.RESTRICT)  # TODO check on_delete
    schedule = models.CharField  # will have special format (days and exact times)
    start_date = models.DateField
    end_date = models.DateField  # TODO is it needed?
    telegram_chat_url = models.URLField  # group chat created manually by the coordinator/teacher

    # related_name must be given, otherwise a backref clash will occur
    coordinators = models.ManyToManyField(Person, related_name="groups_as_coordinator")
    students = models.ManyToManyField(Person, related_name="groups_as_student")
    teachers = models.ManyToManyField(Person, related_name="groups_as_teacher")

    # TODO __str__(self): how to join self.teachers?
