import uuid

from django.db import models


class MultilingualModel(models.Model):
    """Abstract model for end-user facing entities that need names to be stored in 3 languages."""

    name_internal = models.CharField(
        max_length=50,
        unique=True,
        help_text=(
            "Internal name to use in code. This will allow to change user-facing names easily "
            "without breaking the code."
        ),
    )
    name_en = models.CharField(max_length=255, unique=True)
    name_ru = models.CharField(max_length=255, unique=True)
    name_ua = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True  # This model will not be used to create any database table


class InternalModelWithName(models.Model):
    """Abstract model for internal entities that have a name attribute but do not need to support
    internationalization.
    """

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


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

    # this can be tracked via LogEvents but an additional column can be a convenient shortcut:
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


# SOURCE OF INFORMATION ABOUT THE SCHOOL
class InformationSource(MultilingualModel):
    """Model for enumerating possible sources of information about SSG (answer to the question
    'How did you find out about us?').
    """


# PEOPLE
# One person can perform several roles.  Therefore, the logic proposed is as follows: first,
# a PersonalInfo is created, then e.g. a Coordinator is created, linking to that PersonalInfo.
# Then, if the same person assumes another role, e.g. a Teacher is created, linking to the
# existing PersonalInfo.
class PersonalInfo(models.Model):
    """Model for storing personal information that is relevant for all roles
    (coordinators, students and teachers).
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
    approximate_date_of_birth = models.DateField()  # TODO still undecided if we use this or age

    information_source = models.ForeignKey(
        InformationSource,
        on_delete=models.PROTECT,
        verbose_name="how did they learn about Samantha Smith's Group?",
    )
    native_languages = models.ManyToManyField(NativeLanguage)  # a person can be bilingual
    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    # these are none for coordinator, but can be present for student/teacher, so keeping them here
    registration_bot_chat_id = models.IntegerField(blank=True, null=True)
    chatwoot_conversation_id = models.IntegerField(blank=True, null=True)

    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("last_name", "first_name")  # TODO this could be used for selection algorithm

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Coordinator(models.Model):
    """Model for a coordinator."""

    # We want to give informative related_name (PersonalInfo.coordinator will be misleading),
    # so an abstract model with personal_info is out of the question.
    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_coordinator",
    )
    is_admin = models.BooleanField(
        default=False,
        help_text=(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
    status = models.ForeignKey(CoordinatorStatus, on_delete=models.PROTECT)

    def __str__(self):
        role = "Admin" if self.is_admin else "Coordinator"
        return f"{role} {self.personal_info.full_name}"


class Student(models.Model):
    """Model for a student."""

    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_student",
    )

    requires_communication_in_ukrainian = models.BooleanField(default=False)

    # these are all statuses, but `status` is a complex one concerning working in groups
    # (i.e. the main activity of the school) and the other two are simple yes-or-no statuses
    is_member_of_speaking_club = models.BooleanField(
        default=False,
        verbose_name="Speaking club status",
        help_text="Is the student a member of a speaking club at the moment?",
    )
    requires_help_with_CV = models.BooleanField(
        default=False,
        verbose_name="CV help status",
        help_text="Does the student need help with CV at the moment?",
    )
    status = models.ForeignKey(
        StudentStatus,
        on_delete=models.PROTECT,
        verbose_name="Group studies status",
        help_text="Status of a student with regard to group studies",
    )

    # The general rule is that one student can only learn one language,
    # but we don't want to limit this in the database.
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)

    def __str__(self):
        return f"Student {self.personal_info.full_name}"


class TeacherCategory(MultilingualModel):
    """Model for enumerating categories of a teacher (teacher, methodist, CV mentor etc.)."""


class Teacher(models.Model):
    """Model for a teacher."""

    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_teacher",
    )
    status = models.ForeignKey(TeacherStatus, on_delete=models.PROTECT)
    categories = models.ManyToManyField(TeacherCategory)
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)

    def __str__(self):
        return f"Teacher {self.personal_info.full_name}"


# LOG EVENTS
# We could have created one table listing all possible names of log events, but that might look
# confusing for admin users later on.  It seems more convenient for them to have separate tables.


class CoordinatorLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a coordinator."""


class GroupLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a group."""


class StudentLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a student."""


class TeacherLogEventName(InternalModelWithName):
    """Model for enumeration of possible names of log events (events) for a teacher."""


class LogEvent(models.Model):
    """Abstract model for some sort of internal event, e.g. 'joined group' for a
    student or 'finished' for a group. Statuses will be assigned based on these events.

    We don't call the class simply Event for it not to be confused with possible models for events
    organized by the school.
    """

    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PersonLogEvent(LogEvent):
    """Abstract class for a log event concerning a person."""

    from_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_from_self",  # will produce e.g. "studentLogEvents_from_self"
    )
    to_group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="%(class)s_from_self",
    )

    class Meta:
        abstract = True


class GroupLogEvent(LogEvent):
    group = models.ForeignKey("Group", on_delete=models.CASCADE)


class CoordinatorLogEvent(LogEvent):
    name = models.ForeignKey(CoordinatorLogEventName, on_delete=models.CASCADE)
    coordinator_info = models.ForeignKey(Coordinator, related_name="log", on_delete=models.CASCADE)


class StudentLogEvent(LogEvent):
    name = models.ForeignKey(StudentLogEventName, on_delete=models.CASCADE)
    student_info = models.ForeignKey(Student, related_name="log", on_delete=models.CASCADE)


class TeacherLogEvent(LogEvent):
    name = models.ForeignKey(TeacherLogEventName, on_delete=models.CASCADE)
    teacher_info = models.ForeignKey(Teacher, related_name="log", on_delete=models.CASCADE)


# GROUP
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
    student_info = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(EnrollmentTestQuestionOption)
