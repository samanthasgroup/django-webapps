import uuid

from django.db import models


class MultilingualModel(models.Model):
    """Abstract model for end-user facing entities that need names to be stored in 3 languages."""

    # TODO add internal name?
    name_en = models.CharField(max_length=255, unique=True)
    name_ru = models.CharField(max_length=255, unique=True)
    name_ua = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True  # This model will not be used to create any database table


class InternalModelWithName(models.Model):
    """Abstract model for internal entities that have a name attrinute but do not need to support
    internationalization.
    """

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


# TODO check if this must be registered somewhere
class AdminSiteUser(models.Model):
    login = models.CharField(max_length=70, unique=True)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.full_name} (login {self.login})"


# LANGUAGES AND LEVELS
class NativeLanguage(MultilingualModel):
    """Model for native languages of coordinators, students and teachers."""


class TeachingLanguage(MultilingualModel):
    """Model for languages that students learn and teachers teach."""


class LanguageLevel(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rank = models.IntegerField(unique=True)


class TeachingLanguageAndLevel(models.Model):
    language = models.ForeignKey(TeachingLanguage, on_delete=models.CASCADE)
    level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE)


# DAYS OF WEEK AND TIME SLOTS
class DayOfWeek(MultilingualModel):
    """Model for days of the week (with internationalization)."""

    # We could just use numbers and then localize them using Babel,
    # but it seems easier to just create a table with 7 rows.


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
# We could have created one table listing all possible status names, but that might look confusing
# for admin users later on.  It seems more convenient for them to have separate tables.
class CoordinatorStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a coordinator."""


class GroupStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a group."""


class StudentStatusName(InternalModelWithName):
    """Model for enumeration of possible statuses of a student."""


class TeacherStatusName(InternalModelWithName):
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

    is_admin = models.BooleanField(
        default=False,
        help_text=(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
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


class TeacherCategory(MultilingualModel):
    """Model for enumerating categories of a teacher (teacher, methodist, CV mentor etc.)."""


class TeacherInfo(models.Model):
    """Additional information about a teacher. If an instance of Person has this attribute, this
    person is a teacher.
    """

    status = models.ForeignKey(TeacherStatus, on_delete=models.PROTECT)
    categories = models.ManyToManyField(TeacherCategory)
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)


# LOG ITEMS (EVENTS)
# We could have created one table listing all possible names of log items, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class CoordinatorLogItemName(InternalModelWithName):
    """Model for enumeration of possible names of log items (events) for a coordinator."""


class GroupLogItemName(InternalModelWithName):
    """Model for enumeration of possible names of log items (events) for a group."""


class StudentLogItemName(InternalModelWithName):
    """Model for enumeration of possible names of log items (events) for a student."""


class TeacherLogItemName(InternalModelWithName):
    """Model for enumeration of possible names of log items (events) for a teacher."""


class LogItem(models.Model):
    """Abstract model for some sort of internal event ('log item'), e.g. 'joined group' for a
    student or 'finished' for a group. Statuses will be assigned based on these events.

    We don't call the class Event (although it is an event in a programming sense) for it not to be
    confused with possible models for events organized by the school.
    """

    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class GroupLogItem(LogItem):
    group = models.ForeignKey("Group", on_delete=models.CASCADE)


class CoordinatorLogItem(LogItem):
    name = models.ForeignKey(CoordinatorLogItemName, on_delete=models.CASCADE)
    coordinator_info = models.ForeignKey(
        CoordinatorInfo, related_name="log", on_delete=models.CASCADE
    )
    from_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="coordinator_log_from_self",
    )
    to_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="coordinator_log_to_self",
    )


class StudentLogItem(LogItem):
    name = models.ForeignKey(StudentLogItemName, on_delete=models.CASCADE)
    student_info = models.ForeignKey(StudentInfo, related_name="log", on_delete=models.CASCADE)
    from_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="student_log_from_self",
    )
    to_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="student_log_to_self",
    )


class TeacherLogItem(LogItem):
    name = models.ForeignKey(TeacherLogItemName, on_delete=models.CASCADE)
    teacher_info = models.ForeignKey(TeacherInfo, related_name="log", on_delete=models.CASCADE)
    from_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="teacher_log_from_self",
    )
    to_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="teacher_log_to_self",
    )


# SOURCE OF INFORMATION ABOUT THE SCHOOL
class InformationSource(MultilingualModel):
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

    information_source = models.ForeignKey(
        InformationSource,
        on_delete=models.PROTECT,
        verbose_name="how did they learn about Samantha Smith's Group?",
    )
    # a person can be bilingual
    native_language = models.ManyToManyField(NativeLanguage)
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
        verbose_name="block of coordinator-specific information, if this person is a coordinator",
    )
    student_info = models.OneToOneField(
        "StudentInfo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="block of student-specific information, if this person is a student",
    )
    teacher_info = models.OneToOneField(
        "TeacherInfo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="block of teacher-specific information, if this person is a teacher",
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
    text = models.CharField(max_length=255, unique=True)


class EnrollmentTestQuestionOption(models.Model):
    question = models.ForeignKey(EnrollmentTestQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=50, unique=True)
    is_correct = models.BooleanField()


class EnrollmentTestResult(models.Model):
    student_info = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)
