from datetime import timedelta

from django.db import migrations, models
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.db.models import Q
from faker import Faker
from model_bakery.recipe import Recipe, foreign_key

from api.models import AgeRange, DayAndTimeSlot, NonTeachingHelp, LanguageAndLevel
from api.models.choices.age_range_type import AgeRangeType
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.registration_telegram_bot_language import (
    RegistrationTelegramBotLanguage,
)
from api.models.choices.statuses import CoordinatorStatus, StudentStatus, TeacherStatus, TeacherUnder18Status
from api.models.helpers import DataMigrationMaster

APP_NAME = "api"

AMOUNT_OF_COORDINATORS = 10
AMOUNT_OF_STUDENTS = 100
AMOUNT_OF_TEACHERS = 25
AMOUNT_OF_TEACHERS_UNDER_18 = 5


class FakeDataPopulationMaster(DataMigrationMaster):
    def __init__(self, apps: StateApps, schema_editor: DatabaseSchemaEditor):
        super().__init__(apps, schema_editor)
        self.faker: Faker = Faker()
        self.personal_info_recipe = self._make_personal_info_recipe()
        self.coordinator_recipe = self._make_coordinator_recipe()
        self.student_recipe = self._make_student_recipe()
        self.teacher_recipe = self._make_teacher_recipe()
        self.teacher_under_18_recipe = self._make_teacher_under_18_recipe()

    def _get_random_amount_of_objects(
        self,
        model: type[models.Model],
        filter_condition: Q = Q(),
        min_length: int = 0,
        max_length: int | None = None,
    ) -> models.QuerySet:
        """Returns a random amount of objects from the database as a queryset."""
        queryset = model.objects.filter(filter_condition)
        if max_length is None:
            max_length = queryset.count()
        return self.faker.random_choices(
            queryset,
            length=self.faker.pyint(min_value=min_length, max_value=max_length),
        )

    def _make_personal_info_recipe(self):
        return Recipe(
            APP_NAME + ".PersonalInfo",
            # These are callables from faker to be called on recipe baking
            first_name=self.faker.first_name,
            last_name=self.faker.last_name,
            email=self.faker.email,
            communication_language_mode=self.faker.random_element(
                CommunicationLanguageMode.values
            ),
            telegram_username=self.faker.user_name,
            phone=self.faker.numerify("+3531#######"),
            information_source=self.faker.text,
            registration_telegram_bot_chat_id=self.faker.pyint,
            # If we don't use lambda here, then the same value will be used for all instances
            registration_telegram_bot_language=lambda: self.faker.random_element(
                RegistrationTelegramBotLanguage.values
            ),
            chatwoot_conversation_id=self.faker.pyint,
            utc_timedelta=lambda: timedelta(
                self.faker.pyint(min_value=-12, max_value=12)
            ),
        )

    def _make_coordinator_recipe(self):
        return Recipe(
            APP_NAME + ".Coordinator",
            personal_info=foreign_key(self.personal_info_recipe, one_to_one=True),
            comment=self.faker.text,
            is_admin=self.faker.pybool,
            is_validated=self.faker.pybool,
            status=lambda: self.faker.random_element(CoordinatorStatus.values),
        )

    def _make_student_recipe(self):
        return Recipe(
            APP_NAME + ".Student",
            personal_info=foreign_key(self.personal_info_recipe, one_to_one=True),
            comment=self.faker.text,
            status=lambda: self.faker.random_element(StudentStatus.values),
            age_range=lambda: self.faker.random_element(AgeRange.objects.filter(type=AgeRangeType.STUDENT)),
            # TODO think about this lambdas and how to make them better
            availability_slots=lambda: self._get_random_amount_of_objects(
                DayAndTimeSlot, min_length=10, max_length=20
            ),
            can_read_in_english=self.faker.pybool,
            is_member_of_speaking_club=self.faker.pybool,
            non_teaching_help_required=lambda: self._get_random_amount_of_objects(
                NonTeachingHelp
            ),
            smalltalk_test_result=self.faker.json,
            teaching_languages_and_levels=lambda: self._get_random_amount_of_objects(
                LanguageAndLevel
            ),
        )

    def _make_teacher_recipe(self):
        """Makes fake teachers."""
        return Recipe(
            APP_NAME + ".Teacher",
            personal_info=foreign_key(self.personal_info_recipe, one_to_one=True),
            comment=self.faker.text,
            status=lambda: self.faker.random_element(TeacherStatus.values),
            can_host_speaking_club=self.faker.pybool,
            has_hosted_speaking_club=self.faker.pybool,
            is_validated=self.faker.pybool,
            availability_slots=lambda: self._get_random_amount_of_objects(
                DayAndTimeSlot, min_length=10, max_length=20
            ),
            non_teaching_help_provided=lambda: self._get_random_amount_of_objects(
                NonTeachingHelp
            ),
            peer_support_can_check_syllabus=self.faker.pybool,
            peer_support_can_host_mentoring_sessions=self.faker.pybool,
            peer_support_can_give_feedback=self.faker.pybool,
            peer_support_can_help_with_childrens_groups=self.faker.pybool,
            peer_support_can_provide_materials=self.faker.pybool,
            peer_support_can_invite_to_class=self.faker.pybool,
            peer_support_can_work_in_tandem=self.faker.pybool,
            simultaneous_groups=self.faker.pyint,
            student_age_ranges=lambda: self._get_random_amount_of_objects(
                AgeRange, filter_condition=Q(type=AgeRangeType.TEACHER)
            ),
            teaching_languages_and_levels=lambda: self._get_random_amount_of_objects(
                LanguageAndLevel
            ),
            weekly_frequency_per_group=self.faker.pyint,
        )

    def _make_teacher_under_18_recipe(self):
        return Recipe(
            # TODO: Think about recipe inheritance for Teacher, Person
            #  (https://model-bakery.readthedocs.io/en/latest/recipes.html#recipe-inheritance)
            APP_NAME + ".TeacherUnder18",
            personal_info=foreign_key(self.personal_info_recipe, one_to_one=True),
            comment=self.faker.text,
            status=lambda: self.faker.random_element(TeacherUnder18Status.values),
            can_host_speaking_club=self.faker.pybool,
            has_hosted_speaking_club=self.faker.pybool,
            is_validated=self.faker.pybool,
        )

    def _make_fake_coordinators(self):
        """Makes fake coordinators."""
        self.coordinator_recipe.make(_quantity=AMOUNT_OF_COORDINATORS)

    def _make_fake_students(self):
        """Makes fake students."""
        self.student_recipe.make(_quantity=AMOUNT_OF_STUDENTS)

    def _make_fake_teachers(self):
        """Makes fake teachers."""
        self.teacher_recipe.make(_quantity=AMOUNT_OF_TEACHERS)

    def _make_fake_teachers_under_18(self):
        """Makes fake teachers under 18."""
        self.teacher_under_18_recipe.make(_quantity=AMOUNT_OF_TEACHERS_UNDER_18)

    def main(self):
        """Runs pre-population operations."""
        self._make_fake_students()
        self._make_fake_coordinators()
        self._make_fake_teachers()
        self._make_fake_teachers_under_18()
        # TODO Groups


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_data_migration"),
    ]

    operations = [
        migrations.RunPython(
            FakeDataPopulationMaster.run, reverse_code=migrations.RunPython.noop
        )
    ]
