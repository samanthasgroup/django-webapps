import uuid
from datetime import timedelta

from django.db import models

from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import CommunicationLanguageMode, TeachingLanguageAndLevel
from api.models.statuses import CoordinatorStatus, StudentStatus, TeacherStatus


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
    utc_timedelta = models.DurationField(default=timedelta(hours=0))

    information_source = models.TextField(
        verbose_name="how did they learn about Samantha Smith's Group?"
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)
    communication_language_mode = models.ForeignKey(
        CommunicationLanguageMode, on_delete=models.PROTECT
    )

    # These are none for coordinator, but can be present for student/teacher, so keeping them here.
    # Also, there is a possibility that coordinators will register with registration bot someday.
    registration_bot_chat_id = models.IntegerField(blank=True, null=True)
    chatwoot_conversation_id = models.IntegerField(blank=True, null=True)

    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("last_name", "first_name")  # TODO this could be used for selection algorithm

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AgeRange(models.Model):
    """Model for age range.  Students have no exact ages, but age ranges. Teachers' preferences
    and group building algorithms are also based on age ranges.
    """

    age_from = models.IntegerField()
    age_to = models.IntegerField()

    def __str__(self):
        return f"Age {self.age_from} to {self.age_to}"


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

    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text="We do not ask students for their exact age. "
        "They choose an age range when registering with us.",
    )

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


class Teacher(models.Model):
    """Model for a teacher."""

    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_teacher",
    )
    has_prior_teaching_experience = models.BooleanField()
    simultaneous_groups = models.IntegerField(
        default=1, help_text="Number of groups the teacher can teach simultaneously"
    )
    status = models.ForeignKey(TeacherStatus, on_delete=models.PROTECT)
    student_age_ranges = models.ManyToManyField(
        AgeRange,
        help_text="Age ranges of students that the teacher is willing to teach. "
        "The 'from's and 'to's of these ranges are wider than those the students choose "
        "for themselves.",
    )
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)
    weekly_frequency_per_group = models.IntegerField(
        help_text="Number of times per week the teacher can have classes with each group"
    )

    def __str__(self):
        return f"Teacher {self.personal_info.full_name}"
