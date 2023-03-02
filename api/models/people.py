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
    """Model for storing personal information that does not depend on a person's role
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
        verbose_name_plural = "personal info records"

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


class Person(models.Model):
    """Abstract model for a coordinator/student/teacher. Stores their common fields and methods."""

    personal_info = models.OneToOneField(
        PersonalInfo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="as_%(class)s",  # produces `.as_coordinator` etc.
    )

    # Statuses are different for different roles, but this automatic field is common for them all.
    # Date and time of status change can be tracked in LogEvents but this is a convenient shortcut.
    status_since = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return (
            f"{self.personal_info.full_name}. Status: {getattr(self, 'status')} "
            f"(since {getattr(self, 'status_since').strftime('%H:%M %d.%m.%Y')})"
        )


class Coordinator(Person):
    """Model for a coordinator."""

    is_admin = models.BooleanField(
        default=False,
        help_text=(
            "This field has nothing to do with accessing Django admin site. It marks coordinators "
            "that have special rights over ordinary coordinators."
        ),
    )
    status = models.ForeignKey(CoordinatorStatus, on_delete=models.PROTECT)

    def __str__(self):
        role = " (admin)" if self.is_admin else ""
        return f"{super().__str__()}{role}"


class Student(Person):
    """Model for a student."""

    age_range = models.ForeignKey(
        AgeRange,
        on_delete=models.PROTECT,
        help_text="We do not ask students for their exact age. "
        "They choose an age range when registering with us.",
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)

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


class Teacher(Person):
    """Model for a teacher."""

    additional_skills_comment = models.CharField(
        max_length=255,  # prefer this to TextField for a better search
        blank=True,
        null=True,
        verbose_name="Comment on additional skills besides teaching",
        help_text="other ways in which the applicant could help, besides teaching or helping other"
        "teachers with materials or feedback (comment)",
    )
    availability_slots = models.ManyToManyField(DayAndTimeSlot)

    can_help_with_cv = models.BooleanField(default=False)
    can_help_with_speaking_club = models.BooleanField(default=False)

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
        help_text="Has the applicant already worked as a teacher before applying at Samantha "
        "Smith's Group?",
    )
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
