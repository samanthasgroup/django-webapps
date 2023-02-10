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


# PEOPLE
class Person(models.Model):
    # This is the ID that will identify a person with any role (student, teacher, coordinator),
    # even if one person combines several roles.
    # TODO I guess I'll need a timestamp then because I can't sort by ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)  # can include middle name if a person wishes so
    last_name = models.CharField(max_length=100)
    tg_username = models.CharField
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    tz_summer_relative_to_utc = models.IntegerField
    tz_winter_relative_to_utc = models.IntegerField
    approximate_date_of_birth = models.DateField

    enrolment_bot_chat_id = models.IntegerField  # TODO none for coordinator; move to info?
    chatwoot_conversation_id = models.IntegerField  # TODO none for coordinator; move to info?

    # If this is a student, we will not allow them to select more than 1 language at registration,
    # but the database will remain agnostic: any person can be related to any number of languages
    # and levels.

    # native_language = models.ForeignKey  # TODO
    # status = models.ForeignKey  # TODO
    # availability_slots = models.ForeignKey  # TODO
    # source  # TODO: how they learned about SSG

    # blank = True and null = True mean that this attribute is optional
    coordinator_info = models.OneToOneField(
        "CoordinatorInfo",
        on_delete=models.CASCADE,
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


class CoordinatorInfo(models.Model):
    """Additional information about a coordinator. If an instance of Person has this attribute,
    this person is a coordinator.
    """

    is_admin = models.BooleanField(default=False)


class StudentInfo(models.Model):
    """Additional information about a student. If an instance of Person has this attribute, this
    person is a student.
    """

    requires_communication_in_ukrainian = models.BooleanField
    is_member_of_speaking_club = models.BooleanField
    needs_help_with_CV = models.BooleanField
    # right now a student can only learn 1 language, but we don't want to fix this in the database
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)


class TeacherInfo(models.Model):
    """Additional information about a teacher. If an instance of Person has this attribute, this
    person is a teacher.
    """

    # teacher_categories = models.ManyToManyField  # TODO
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)


class Group(models.Model):
    start_date = models.DateField
    end_date = models.DateField  # Is it needed?

    language_and_level = models.ForeignKey(TeachingLanguageAndLevel, on_delete=models.CASCADE)

    # related_name must be given, otherwise a backref clash will occur
    coordinators = models.ManyToManyField(Person, related_name="groups_as_coordinator")
    students = models.ManyToManyField(Person, related_name="groups_as_student")
    teachers = models.ManyToManyField(Person, related_name="groups_as_teacher")

    # TODO __str__(self): how to join self.teachers?
