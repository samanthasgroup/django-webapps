import uuid

from django.db import models

from api.models.auxil import MultilingualModel
from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import NativeLanguage, TeachingLanguageAndLevel
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
    # TODO leave only one offset, not integer anymore?
    tz_summer_relative_to_utc = models.IntegerField()
    tz_winter_relative_to_utc = models.IntegerField()
    # TODO for teachers, we don't store age.
    approximate_date_of_birth = models.DateField()  # TODO still undecided if we use this or age

    information_source = models.TextField(
        verbose_name="how did they learn about Samantha Smith's Group?"
    )
    native_languages = models.ManyToManyField(NativeLanguage)  # TODO remove this and the model?
    # TODO communication_language (ru, ua, any, l2 only)
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

    # TODO preferred language of communication: ru, ua, any, l2_only
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
    # TODO has_prior_teaching_experience
    # TODO how many groups can take

    def __str__(self):
        return f"Teacher {self.personal_info.full_name}"
