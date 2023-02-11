import uuid

from django.db import models


class MultilingualObject(models.Model):
    # TODO add internal name?
    name_en = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_ua = models.CharField(max_length=255)

    class Meta:
        abstract = True  # This model will not be used to create any database table


class AdminSiteUser(models.Model):
    login = models.CharField(max_length=70)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


# LANGUAGES AND LEVELS
class NativeLanguage(MultilingualObject):
    ...


class TeachingLanguage(MultilingualObject):
    ...


class LanguageLevel(models.Model):
    name = models.CharField(max_length=3)
    rank = models.IntegerField()


class TeachingLanguageAndLevel(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)


# DAYS OF WEEK AND TIME SLOTS
class DayOfWeek(MultilingualObject):
    # We could just use numbers and then localize them using Babel,
    # but it seems easier to just create a table with 7 rows.
    ...


class TimeSlot(models.Model):
    # Postgres supports ranges, and in Django we could use IntegerRangeField for a Postgres range,
    # but that would hinder development and testing with SQLite.
    # Also, Postgres has no pure time ranges (only date-time).
    from_utc_hour = models.TimeField()
    to_utc_hour = models.TimeField()


class DayAndTimeSlot(models.Model):
    day_of_week = models.ForeignKey(DayOfWeek, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)


# STATUSES
class StatusName(models.Model):
    """Abstract model for classes enumerating possible statuses."""

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


# We could create one table listing all possible status names, but that might look confusing
# for admin users later on.  It seems more convenient for them to have separate tables.
class CoordinatorStatusName(StatusName):
    """Model for enumeration of possible statuses of a coordinator."""


class GroupStatusName(StatusName):
    """Model for enumeration of possible statuses of a group."""


class StudentStatusName(StatusName):
    """Model for enumeration of possible statuses of a student."""


class TeacherStatusName(StatusName):
    """Model for enumeration of possible statuses of a teacher."""


class Status(models.Model):
    """Abstract model for an actual status of a group or person. Combines a status name
    (selected from allowed status names) with a time that indicates when this status was assigned.
    """

    # this can be tracked via LogItems but an additional column can be a very convenient shortcut:
    in_place_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CoordinatorStatus(Status):
    """Model for statuses of coordinators."""

    name = models.ForeignKey(CoordinatorStatusName, on_delete=models.CASCADE)


class GroupStatus(Status):
    """Model for statuses of groups."""

    name = models.ForeignKey(GroupStatusName, on_delete=models.CASCADE)


class StudentStatus(Status):
    """Model for statuses of students."""

    name = models.ForeignKey(StudentStatusName, on_delete=models.CASCADE)


class TeacherStatus(Status):
    """Model for statuses of teachers."""

    name = models.ForeignKey(TeacherStatusName, on_delete=models.CASCADE)


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

    is_member_of_speaking_club = models.BooleanField(default=False)
    requires_help_with_CV = models.BooleanField(default=False)
    requires_communication_in_ukrainian = models.BooleanField(default=False)
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
    type = models.CharField(max_length=100)
    # TODO add accepted events to another table or just create an Enum?

    class Meta:
        abstract = True


class GroupLogItem(LogItem):
    group = models.ForeignKey("Group", on_delete=models.CASCADE)


class CoordinatorLogItem(models.Model):
    coordinator_info = models.ForeignKey(
        CoordinatorInfo, related_name="log", on_delete=models.CASCADE
    )
    # TODO these should be optional (in other classes too) because either from or to could be empty
    from_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="coordinator_log_from_self"
    )
    to_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="coordinator_log_to_self"
    )


class StudentLogItem(models.Model):
    student_info = models.ForeignKey(StudentInfo, related_name="log", on_delete=models.CASCADE)
    from_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="student_log_from_self"
    )
    to_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="student_log_to_self"
    )


class TeacherLogItem(models.Model):
    teacher_info = models.ForeignKey(TeacherInfo, related_name="log", on_delete=models.CASCADE)
    from_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="teacher_log_from_self"
    )
    to_group = models.ForeignKey(
        "Group", on_delete=models.CASCADE, related_name="teacher_log_to_self"
    )


# SOURCE OF INFORMATION ABOUT THE SCHOOL
class InformationSource(MultilingualObject):
    """Model for enumerating possible sources of information about SSG (answer to the question
    'How did you find out about us?').
    """


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
    # Telegram's limit is 32, but this might change
    tg_username = models.CharField(blank=True, max_length=100, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    tz_summer_relative_to_utc = models.IntegerField()
    tz_winter_relative_to_utc = models.IntegerField()
    approximate_date_of_birth = models.DateField()

    information_source = models.ForeignKey(InformationSource, on_delete=models.PROTECT)
    native_language = models.ForeignKey(NativeLanguage, on_delete=models.PROTECT)
    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    # these are none for coordinator, but can be present for student/teacher, so keeping them here
    registration_bot_chat_id = models.IntegerField(blank=True, null=True)
    chatwoot_conversation_id = models.IntegerField(blank=True, null=True)

    # The logic is that if a person has coordinator_info, they are a coordinator, etc.
    # blank = True and null = True mean that this attribute is optional.
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

    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        # TODO display whether it's a teacher, a student, a coordinator, or a combination of these
        return f"{self.first_name} {self.last_name}"


class Group(models.Model):
    availability_slot = models.ManyToManyField(DayAndTimeSlot)
    is_for_staff_only = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.CASCADE)
    status = models.ForeignKey(GroupStatus, on_delete=models.PROTECT)
    start_date = models.DateField(blank=True, null=True)
    # this field could be useful for overview, but can be filled automatically when
    # a corresponding log item is created:
    end_date = models.DateField(blank=True, null=True)
    # group chat created manually by the coordinator/teacher
    telegram_chat_url = models.URLField(blank=True, null=True)

    # related_name must be given, otherwise a backref clash will occur
    coordinators = models.ManyToManyField(Person, related_name="groups_as_coordinator")
    students = models.ManyToManyField(Person, related_name="groups_as_student")
    teachers = models.ManyToManyField(Person, related_name="groups_as_teacher")

    # some research showed that it's better to store the schedule not in a single text field
    # with some pre-defined syntax, but in 7 columns, one per day of the week
    monday = models.TimeField(blank=True, null=True)
    tuesday = models.TimeField(blank=True, null=True)
    wednesday = models.TimeField(blank=True, null=True)
    thursday = models.TimeField(blank=True, null=True)
    friday = models.TimeField(blank=True, null=True)
    saturday = models.TimeField(blank=True, null=True)
    sunday = models.TimeField(blank=True, null=True)

    # TODO __str__(self): how to join self.teachers?


# ENROLLMENT TEST
class EnrollmentTest(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.PROTECT)
    levels = models.ManyToManyField(LanguageLevel)


class EnrollmentTestQuestion(models.Model):
    enrollment_test = models.ForeignKey(EnrollmentTest, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)


class EnrollmentTestQuestionOption(models.Model):
    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    is_correct = models.BooleanField()


class EnrollmentTestResult(models.Model):
    student_info = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)
