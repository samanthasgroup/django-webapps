import sys
from datetime import timedelta, time

from django.db import migrations, models, DatabaseError
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.db.models import Q
from faker import Faker
from model_bakery.recipe import Recipe, foreign_key, related

from api.models import (
    AgeRange,
    DayAndTimeSlot,
    NonTeachingHelp,
    LanguageAndLevel,
    Language,
)
from api.models.choices.age_range_type import AgeRangeType
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.registration_telegram_bot_language import (
    RegistrationTelegramBotLanguage,
)
from api.models.choices.statuses import (
    CoordinatorStatus,
    StudentStatus,
    TeacherStatus,
    TeacherUnder18Status,
    GroupStatus,
)
from api.models.data_populator import DataPopulator

APP_NAME = "api"

AMOUNT_OF_COORDINATORS_WITHOUT_GROUP = 10
AMOUNT_OF_GROUPS = 30
AMOUNT_OF_STUDENTS_WITHOUT_GROUP = 30
AMOUNT_OF_TEACHERS_WITHOUT_GROUP = 5
AMOUNT_OF_TEACHERS_UNDER_18_WITHOUT_SPEAKING_CLUB = 5
AMOUNT_OF_SPEAKING_CLUBS = 7

MIN_AMOUNT_OF_COORDINATORS_IN_GROUP = 1
MAX_AMOUNT_OF_COORDINATORS_IN_GROUP = 2

MIN_AMOUNT_OF_STUDENTS_IN_GROUP = 2
MAX_AMOUNT_OF_STUDENTS_IN_GROUP = 10

MIN_AMOUNT_OF_TEACHERS_IN_GROUP = 1
MAX_AMOUNT_OF_TEACHERS_IN_GROUP = 2

MIN_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB = 1
MAX_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB = 2


class RecipeStorage:
    """Helper class for producing recipes with fake data.

    For the sake of readability, this class is separated from class
    that populates database data produced from these recipes.
    """

    def __init__(self):
        self.faker: Faker = Faker()
        self.personal_info = self._make_personal_info_recipe()
        self.coordinator = self._make_coordinator_recipe()
        self.student = self._make_student_recipe()
        self.teacher = self._make_teacher_recipe()
        self.teacher_under_18 = self._make_teacher_under_18_recipe()
        self.group = self._make_group_recipe()
        self.speaking_club = self._make_speaking_club_recipe()

    def _get_random_time_or_none(self) -> time | None:
        return self.faker.random_element([None, self.faker.time_object()])

    def _get_group_days_of_week(self) -> dict[str, time | None]:
        return {
            day_name.lower(): lambda: self._get_random_time_or_none()
            for day_name in DayAndTimeSlot.DayOfWeek.labels
        }

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

    def _make_group_common_recipe(
        self,
        model_name: str,
    ) -> Recipe:
        return Recipe(
            model_name,
            # For m2m fields, we need to use related() with args of m2m objects' recipes
            coordinators=lambda: related(
                *[self.coordinator]
                * self.faker.pyint(
                    min_value=MIN_AMOUNT_OF_COORDINATORS_IN_GROUP,
                    max_value=MAX_AMOUNT_OF_COORDINATORS_IN_GROUP,
                )
            ),
            students=lambda: related(
                *[self.student]
                * self.faker.pyint(
                    min_value=MIN_AMOUNT_OF_STUDENTS_IN_GROUP,
                    max_value=MAX_AMOUNT_OF_STUDENTS_IN_GROUP,
                )
            ),
            teachers=lambda: related(
                *[self.teacher]
                * self.faker.pyint(
                    min_value=MIN_AMOUNT_OF_TEACHERS_IN_GROUP,
                    max_value=MAX_AMOUNT_OF_TEACHERS_IN_GROUP,
                )
            ),
            telegram_chat_url=self.faker.url,
        )

    def _make_personal_info_recipe(self) -> Recipe:
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
            # TODO think about these lambdas and how to make it more beautiful
            registration_telegram_bot_language=lambda: self.faker.random_element(
                RegistrationTelegramBotLanguage.values
            ),
            chatwoot_conversation_id=self.faker.pyint,
            utc_timedelta=lambda: timedelta(
                hours=self.faker.pyint(min_value=-12, max_value=12), minutes=self.faker.random_element([0, 30])
            ),
        )

    def _make_coordinator_recipe(self) -> Recipe:
        return Recipe(
            APP_NAME + ".Coordinator",
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            is_admin=self.faker.pybool,
            is_validated=self.faker.pybool,
            status=lambda: self.faker.random_element(CoordinatorStatus.values),
        )

    def _make_student_recipe(self) -> Recipe:
        return Recipe(
            APP_NAME + ".Student",
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            status=lambda: self.faker.random_element(StudentStatus.values),
            age_range=lambda: self.faker.random_element(
                AgeRange.objects.filter(type=AgeRangeType.STUDENT)
            ),
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
                LanguageAndLevel, max_length=2
            ),
        )

    def _make_teacher_recipe(self) -> Recipe:
        """Makes fake teachers."""
        return Recipe(
            APP_NAME + ".Teacher",
            personal_info=foreign_key(self.personal_info, one_to_one=True),
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

    def _make_teacher_under_18_recipe(self) -> Recipe:
        return Recipe(
            # TODO: Think about recipe inheritance for Teacher, Person. See example with Group/SpeakingClub
            #  (https://model-bakery.readthedocs.io/en/latest/recipes.html#recipe-inheritance)
            APP_NAME + ".TeacherUnder18",
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            status=lambda: self.faker.random_element(TeacherUnder18Status.values),
            can_host_speaking_club=self.faker.pybool,
            has_hosted_speaking_club=self.faker.pybool,
            is_validated=self.faker.pybool,
        )

    def _make_group_recipe(self) -> Recipe:
        group_common_recipe = self._make_group_common_recipe(APP_NAME + ".Group")
        return group_common_recipe.extend(
            availability_slot=lambda: self._get_random_amount_of_objects(
                DayAndTimeSlot, min_length=10, max_length=20
            ),
            is_for_staff_only=self.faker.pybool,
            language_and_level=lambda: self.faker.random_element(
                LanguageAndLevel.objects.all()
            ),
            lesson_duration_in_minutes=lambda: self.faker.pyint(
                min_value=30, max_value=120, step=30
            ),
            status=lambda: self.faker.random_element(GroupStatus.values),
            start_date=self.faker.past_date,
            end_date=self.faker.future_date,
            **self._get_group_days_of_week(),
        )

    def _make_speaking_club_recipe(self) -> Recipe:
        group_common_recipe = self._make_group_common_recipe(APP_NAME + ".SpeakingClub")
        return group_common_recipe.extend(
            is_for_children=self.faker.pybool,
            language=lambda: self.faker.random_element(Language.objects.all()),
            teachers_under_18=lambda: related(
                *[self.teacher_under_18]
                * self.faker.pyint(
                    min_value=MIN_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB,
                    max_value=MAX_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB,
                )
            ),
        )


class FakeDataPopulator(DataPopulator):
    def __init__(self, apps: StateApps, schema_editor: DatabaseSchemaEditor) -> None:
        super().__init__(apps, schema_editor)
        self.recipes = RecipeStorage()

    def _make_amount_of_recipe_and_skip_database_error(
        self, recipe: Recipe, amount: int
    ) -> None:
        """
        Ensures that given amount of objects is made.

        While generating objects by recipe, it is possible that some of them will violate any db constraint.
        We need to recreate such objects to skip db constraints and be sure that needed amount is generated.
        """
        for _ in range(amount):
            while True:
                try:
                    recipe.make()
                    break
                except DatabaseError:
                    pass

    def _make_fake_coordinators_without_group(self):
        """Makes fake coordinators without group."""
        self.recipes.coordinator.make(_quantity=AMOUNT_OF_COORDINATORS_WITHOUT_GROUP)

    def _make_fake_students_without_group(self):
        """Makes fake students without group."""
        self.recipes.student.make(_quantity=AMOUNT_OF_STUDENTS_WITHOUT_GROUP)

    def _make_fake_teachers_without_group(self):
        """Makes fake teachers without groups."""
        self.recipes.teacher.make(_quantity=AMOUNT_OF_TEACHERS_WITHOUT_GROUP)

    def _make_fake_teachers_under_18_without_speaking_club(self):
        """Makes fake teachers under 18 without_speaking_club."""
        self.recipes.teacher_under_18.make(
            _quantity=AMOUNT_OF_TEACHERS_UNDER_18_WITHOUT_SPEAKING_CLUB
        )

    def _make_fake_groups(self):
        """Makes fake groups."""
        self._make_amount_of_recipe_and_skip_database_error(
            self.recipes.group, AMOUNT_OF_GROUPS
        )

    def _make_fake_speaking_clubs(self):
        """Makes fake speaking_clubs."""
        self._make_amount_of_recipe_and_skip_database_error(
            self.recipes.speaking_club, AMOUNT_OF_SPEAKING_CLUBS
        )

    def _populate(self):
        """Runs operations required for populating the database with fake data."""
        self._make_fake_students_without_group()
        self._make_fake_coordinators_without_group()
        self._make_fake_teachers_without_group()
        self._make_fake_teachers_under_18_without_speaking_club()
        self._make_fake_groups()
        self._make_fake_speaking_clubs()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_data_migration"),
    ]

    operations = [
        migrations.RunPython(
            FakeDataPopulator.run, reverse_code=migrations.RunPython.noop
        )
    ] if "test" not in " ".join(sys.argv) else []  # Skips this migration in tests
