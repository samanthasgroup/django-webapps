import uuid
from datetime import timedelta

from django.db import models
from phonenumber_field import modelfields

from api.models.age_ranges import AgeRange
from api.models.base import GroupOrPerson
from api.models.constants import (
    DEFAULT_CHAR_FIELD_MAX_LEN,
    DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
    STUDENT_CLASS_MISS_LIMIT,
    CoordinatorGroupLimit,
)
from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import LanguageAndLevel


# PEOPLE
# One person can perform several roles.  Therefore, the logic proposed is as follows: first,
# a PersonalInfo is created, then e.g. a Coordinator is created, linking to that PersonalInfo.
# Then, if the same person assumes another role, e.g. a Teacher is created, linking to the
# existing PersonalInfo.
class PersonalInfo(GroupOrPerson):
    """Model for storing personal information.

    This model does not depend on a person's role (coordinators, students and teachers).
    """

    class RegistrationBotLanguage(models.TextChoices):
        EN = "en", "English"
        RU = "ru", "Russian"
        UA = "ua", "Ukrainian"

    # One ID will identify a person with any role (student, teacher, coordinator),
    # even if one person combines several roles.  The autoincrement simple numeric ID can be used
    # for internal communication ("John 132"), while uuid can be used e.g. for hyperlinks
    # to prevent IDOR
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    # Automatically save date and time when the Person was created.
    date_and_time_added = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)  # can include middle name if a person wishes so
    last_name = models.CharField(max_length=100)
    # Telegram's limit is 32, but this might change
    tg_username = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = modelfields.PhoneNumberField(null=True, blank=True)
    utc_timedelta = models.DurationField(default=timedelta(hours=0))

    information_source = models.TextField(
        verbose_name="source of info about SSG",
        help_text="how did they learn about Samantha Smith's Group?",
    )

    # These are none for coordinator, but can be present for student/teacher, so keeping them here.
    # Also, there is a possibility that coordinators will register with registration bot someday.
    registration_bot_chat_id = models.IntegerField(null=True, blank=True)
    registration_bot_language = models.CharField(
        max_length=2,
        choices=RegistrationBotLanguage.choices,
        help_text="Language in which the person wishes to communicate with the bot "
        "(is chosen by the person at first contact)",
    )
    chatwoot_conversation_id = models.IntegerField(null=True, blank=True)

    class Meta:
        # there may be no phone or tg username, but matching name and email is good enough reason
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "email"], name="full_name_and_email"
            )
        ]
        indexes = [
            models.Index(fields=("last_name", "first_name", "email"), name="name_email_idx")
        ]
        ordering = ("last_name", "first_name")
        verbose_name_plural = "personal info records"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.pk})"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Person(models.Model):
    """Abstract model for a coordinator/student/teacher. Stores their common fields and methods."""

    comment = models.TextField(blank=True)
    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_%(class)s",  # produces `.as_coordinator` etc.
    )

    # TODO last contacted, last responded, scheduled date of next contact?

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.personal_info.full_name}. Status: {getattr(self, 'status')}"


class Coordinator(Person):
    """Model for a coordinator."""

    class Status(models.TextChoices):
        PENDING = "pending", "Completed registration, waiting for onboarding"
        ONBOARDING = "onboarding", "In onboarding"
        ONBOARDING_STALE = (
            "onboarding_stale",
            "Has been in onboarding for too long without taking a group",
        )
        WORKING_BELOW_THRESHOLD = (
            "working_threshold_not_reached",
            "Working, but not yet reached the required minimum amount of groups "
            f"({CoordinatorGroupLimit.MIN})",
        )
        WORKING_OK = "working_ok", "Working, required amount of groups reached"
        WORKING_LIMIT_REACHED = (
            "working_limit_reached",
            f"Working, reached maximum number of groups ({CoordinatorGroupLimit.MAX})",
        )
        ON_LEAVE = "on_leave", "On leave"
        NO_RESPONSE = "no_response", "Not responding"
        LEFT_PREMATURELY = (
            "left_prematurely",
            "Announced that they cannot participate in the project",
        )
        FINISHED_STAYS = "finished_stays", "Finished coordinating but remains in the project"
        FINISHED_LEFT = "finished_left", "Finished coordinating and left the project"
        REMOVED = "removed", "All access revoked, accounts closed"
        BANNED = "banned", "Banned from the project"

    is_admin = models.BooleanField(
        default=False,
        help_text=(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
    mentor = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="interns",
        help_text="mentor of this coordinator. One coordinator can have many interns",
    )
    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=Status.choices
    )

    class Meta:
        indexes = [models.Index(fields=("status",), name="coordinator_status_idx")]

    def __str__(self) -> str:
        role = " (admin)" if self.is_admin else ""
        return f"{super().__str__()}{role}"


class Student(Person):
    """Model for a student."""

    class Status(models.TextChoices):
        AWAITING_OFFER = "awaiting_offer", "Registration complete, waiting for a group"
        GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
        AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
        STUDYING = "study", "Studying in a group"
        NOT_ATTENDING = (
            "not_attending",
            f"Missed {STUDENT_CLASS_MISS_LIMIT} classes in a row without letting the teacher know",
        )
        NEEDS_TRANSFER = "needs_transfer", "Needs transfer to another group"
        NO_RESPONSE = "no_response", "Not responding"
        LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
        FINISHED = "finished", "Completed the course and left the project"
        BANNED = "banned", "Banned from the project"

    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text="We do not ask students for their exact age. "
        "They choose an age range when registering with us.",
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    children = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="parents",
        help_text="children of this student that are also studying at SSG",
    )

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=Status.choices,
        verbose_name="group studies status",
        help_text="status of this student with regard to group studies",
    )
    is_member_of_speaking_club = models.BooleanField(
        default=False,
        verbose_name="Speaking club status",
        help_text="Is the student a member of a speaking club at the moment?",
    )
    requires_help_with_cv = models.BooleanField(
        default=False,
        verbose_name="CV help status",
        help_text="Does the student need help with CV at the moment?",
    )

    # JSONField because this will come from external API, so it's good to be protected from changes
    # Just a reminder: the written test is a model with ForeignKey to Student, no field needed here
    smalltalk_test_result = models.JSONField(
        null=True, blank=True, help_text="JSON received from SmallTalk API"
    )

    # The general rule is that one student can only learn one language,
    # but we don't want to limit this in the database.
    teaching_languages_and_levels = models.ManyToManyField(LanguageAndLevel)

    class Meta:
        indexes = [
            models.Index(fields=("status",), name="student_status_idx"),
        ]


class TeacherCommon(Person):
    """Abstract model for common properties that adult teachers and teachers under 18 share.

    Teachers under 18 cannot teach groups but can some selected activities.
    """

    additional_skills_comment = models.CharField(
        max_length=DEFAULT_CHAR_FIELD_MAX_LEN,  # prefer this to TextField for a better search
        blank=True,
        verbose_name="comment on additional skills besides teaching",
        help_text="other ways in which the applicant could help, besides teaching or helping other"
        "teachers with materials or feedback (comment)",
    )
    can_help_with_speaking_club = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Teacher(TeacherCommon):
    """Model for an adult teacher that can teach groups."""

    class Status(models.TextChoices):
        AWAITING_OFFER = "awaiting_offer", "Registered and waiting for a group"
        GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
        AWAITING_START = "awaiting_start", "Group confirmed, awaiting start of classes"
        TEACHING_ACCEPTING_MORE = "teaching_open", "Teaching, ready to take on another group"
        TEACHING_NOT_ACCEPTING_MORE = "teaching_full", "Teaching, not accepting any more groups"
        TEACHING_ANOTHER_GROUP_OFFERED = (
            "teaching_another_offered",
            "Teaching, received offer for another group",
        )
        TEACHING_AWAITING_START_OF_ANOTHER = (
            "teaching_another_awaiting_start",
            "Teaching, awaiting start of another group",
        )
        NEEDS_SUBSTITUTION = (
            "needs_substitution",
            "Needs a break in teaching the group, substitute teacher needed",
        )
        ON_LEAVE = "on_leave", "On leave"
        NO_RESPONSE = "no_response", "Not responding"
        LEFT_PREMATURELY = (
            "left_prematurely",
            "Announced that they cannot participate in the project",
        )
        FINISHED_LEFT = "finished_left", "Finished teaching and left the project"
        FINISHED_STAYS = "finished_stays", "Finished teaching but remains in the project"
        BANNED = "banned", "Banned from the project"
        REMOVED = "removed", "All access revoked, accounts closed"

    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    can_help_with_cv = models.BooleanField(default=False)

    # Peer help. When a new teacher is added, they cannot have these set to True unless they
    # have prior teaching experience.  However, the `.has_prior_teaching_experience` is meant
    # to stay unchanged (it describes experience before coming to Samantha Smith's Group),
    # while it's imaginable that if a teacher teaches long enough, they will be allowed to consult
    # other teachers.  So these flags being here doesn't really break the 3rd normal form.
    can_check_syllabus = models.BooleanField(default=False)
    can_consult_other_teachers = models.BooleanField(default=False)
    can_give_feedback = models.BooleanField(default=False)
    can_help_with_children_group = models.BooleanField(
        default=False,
        verbose_name="can help with children's groups",
    )
    can_help_with_materials = models.BooleanField(
        default=False, verbose_name="can help with teaching materials"
    )
    can_invite_to_class = models.BooleanField(
        default=False,
        verbose_name="can invite other teachers to their class",
    )
    can_work_in_tandem = models.BooleanField(default=False)

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=Status.choices,
        verbose_name="group studies status",
        help_text="status of this teacher with regard to group studies",
    )
    has_prior_teaching_experience = models.BooleanField(
        default=False,
        help_text="has the applicant already worked as a teacher before applying at Samantha "
        "Smith's Group?",
    )
    simultaneous_groups = models.PositiveSmallIntegerField(
        default=1, help_text="number of groups the teacher can teach simultaneously"
    )
    student_age_ranges = models.ManyToManyField(
        AgeRange,
        help_text="age ranges of students that the teacher is willing to teach. "
        "The 'from's and 'to's of these ranges are wider than those the students choose "
        "for themselves.",
    )
    teaching_languages_and_levels = models.ManyToManyField(LanguageAndLevel)
    weekly_frequency_per_group = models.PositiveSmallIntegerField(
        help_text="number of times per week the teacher can have classes with each group"
    )

    class Meta:
        indexes = [
            models.Index(fields=("status",), name="teacher_status_idx"),
        ]


class TeacherUnder18(TeacherCommon):
    """Model for a teacher under 18 years old that cannot teach groups."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Completed registration in the bot"
        ON_LEAVE = "on_leave", "On leave"
        NO_RESPONSE = "no_response", "Not responding"
        LEFT_PREMATURELY = (
            "left_prematurely",
            "Announced that they cannot participate in the project",
        )
        FINISHED_LEFT = "finished_left", "Finished teaching and left the project"
        FINISHED_STAYS = "finished_stays", "Finished teaching but remains in the project"
        BANNED = "banned", "Banned from the project"
        REMOVED = "removed", "All access revoked, accounts closed"

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH, choices=Status.choices
    )

    class Meta:
        indexes = [models.Index(fields=("status",), name="teacher_under_18_status_idx")]
        verbose_name_plural = "Teaching volunteers under 18 years of age"
