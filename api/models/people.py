import uuid
from datetime import timedelta

from django.db import models
from phonenumber_field import modelfields

from api.models.age_ranges import AgeRange
from api.models.base import GroupOrPerson
from api.models.choices.registration_bot_language import RegistrationBotLanguage
from api.models.choices.statuses import (
    CoordinatorStatus,
    StudentStatus,
    TeacherStatus,
    TeacherUnder18Status,
)
from api.models.constants import (
    DEFAULT_CHAR_FIELD_MAX_LEN,
    DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
    CoordinatorGroupLimit,
)
from api.models.days_time_slots import DayAndTimeSlot
from api.models.languages_levels import LanguageAndLevel
from api.models.non_teaching_help_types import NonTeachingHelpType


# PEOPLE
# One person can perform several roles.  Therefore, the logic proposed is as follows: first,
# a PersonalInfo is created, then e.g. a Coordinator is created, linking to that PersonalInfo.
# Then, if the same person assumes another role, e.g. a Teacher is created, linking to the
# existing PersonalInfo.
class PersonalInfo(GroupOrPerson):
    """Model for storing personal information.

    This model does not depend on a person's role (coordinators, students and teachers).
    """

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

    is_admin = models.BooleanField(
        default=False,
        help_text=(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
    # TODO add default=False when coordinators get an opportunity to register through the bot?
    is_validated = models.BooleanField(
        help_text="Has an initial validation interview been conducted with this teacher?"
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
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=CoordinatorStatus.choices,
    )

    class Meta:
        indexes = [models.Index(fields=("status",), name="coordinator_status_idx")]

    def __str__(self) -> str:
        role = " (admin)" if self.is_admin else ""
        return f"{super().__str__()}{role}"

    @property
    def has_enough_groups(self) -> bool:
        """Returns `True` if coordinator has required minimum amount of groups."""
        if self.group_set.count() >= CoordinatorGroupLimit.MIN:
            return True
        return False

    @property
    def has_reached_group_limit(self) -> bool:
        """Returns `True` if coordinator has reached maximum amount of groups."""
        if self.group_set.count() >= CoordinatorGroupLimit.MAX:
            return True
        return False


class Student(Person):
    """Model for a student."""

    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text="We do not ask students for their exact age. "
        "They choose an age range when registering with us.",
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)
    can_read_in_english = models.BooleanField(null=True, blank=True)
    children = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="parents",
        help_text="children of this student that are also studying at SSG",
    )
    is_member_of_speaking_club = models.BooleanField(
        default=False,
        verbose_name="Speaking club status",
        help_text="Is the student a member of a speaking club at the moment?",
    )
    non_teaching_help_types_required = models.ManyToManyField(
        NonTeachingHelpType,
        blank=True,
        related_name="students",
        verbose_name="Types of non-teaching help this student requires",
    )

    # JSONField because this will come from external API, so it's good to be protected from changes
    # Just a reminder: the written test is a model with ForeignKey to Student, no field needed here
    smalltalk_test_result = models.JSONField(
        null=True, blank=True, help_text="JSON received from SmallTalk API"
    )

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=StudentStatus.choices,
        verbose_name="group studies status",
        help_text="status of this student with regard to group studies",
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
    is_active_in_speaking_club = models.BooleanField(default=False)
    is_validated = models.BooleanField(
        default=False,
        help_text="Has an initial validation interview been conducted with this teacher?",
    )

    class Meta:
        abstract = True


class Teacher(TeacherCommon):
    """Model for an adult teacher that can teach groups."""

    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    non_teaching_help_types_provided = models.ManyToManyField(
        NonTeachingHelpType,
        blank=True,
        related_name="teachers",
        verbose_name="Types of non-teaching help this teacher can provide to students",
    )

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

    has_prior_teaching_experience = models.BooleanField(
        default=False,
        help_text="has the applicant already worked as a teacher before applying at Samantha "
        "Smith's Group?",
    )
    simultaneous_groups = models.PositiveSmallIntegerField(
        default=1, help_text="number of groups the teacher can teach simultaneously"
    )
    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherStatus.choices,
        verbose_name="group studies status",
        help_text="status of this teacher with regard to group studies",
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

    status = models.CharField(
        max_length=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH,
        choices=TeacherUnder18Status.choices,
    )

    class Meta:
        indexes = [models.Index(fields=("status",), name="teacher_under_18_status_idx")]
        verbose_name_plural = "Teaching volunteers under 18 years of age"
