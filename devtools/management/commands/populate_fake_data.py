import sys
from datetime import time, timedelta
from typing import Any, TypeVar

from django.core.management.base import BaseCommand
from django.db import DatabaseError, models, transaction
from django.db.models import Q
from faker import Faker
from model_bakery.recipe import Recipe, foreign_key, related

from api.models import (
    AgeRange,
    Coordinator,
    DayAndTimeSlot,
    Group,
    Language,
    LanguageAndLevel,
    NonTeachingHelp,
    PersonalInfo,
    SpeakingClub,
    Student,
    Teacher,
    TeacherUnder18,
)
from api.models.choices.age_range_type import AgeRangeType
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage
from api.models.choices.status import (
    CoordinatorProjectStatus,
    GroupProjectStatus,
    StudentProjectStatus,
    TeacherProjectStatus,
)

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

M = TypeVar("M", bound=models.Model)


class RecipeStorage:
    """Helper class for producing recipes with fake data."""

    def __init__(self) -> None:
        self.faker: Faker = Faker(locale="uk_UA")
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
        return {member.name.lower(): self._get_random_time_or_none() for member in DayAndTimeSlot.DayOfWeek}

    def _get_random_amount_of_objects(
        self,
        model: type[M],
        filter_condition: Q = Q(),
        min_length: int = 0,
        max_length: int | None = None,
    ) -> list[M]:
        """Returns a random amount of objects from the database as a list."""
        queryset: models.QuerySet[M] = model.objects.filter(filter_condition)  # type: ignore[attr-defined]
        if not queryset.exists():
            return []

        actual_max_length: int = queryset.count()

        # Determine the effective maximum length for pyint
        effective_max_length: int = (
            actual_max_length if max_length is None or max_length > actual_max_length else max_length
        )

        # Determine the effective minimum length for pyint
        # Ensure min_length is not greater than effective_max_length
        effective_min_length: int = min(min_length, effective_max_length)

        if (
            effective_max_length == 0
        ):  # No items to choose from (also covers effective_min_length > effective_max_length implicitly)
            return []

        # Now, effective_min_length <= effective_max_length, and effective_max_length >= 0.
        num_choices = self.faker.pyint(min_value=effective_min_length, max_value=effective_max_length)

        if num_choices == 0:
            return []

        return self.faker.random_choices(
            elements=list(queryset),
            length=num_choices,
        )

    def _make_group_common_recipe(
        self,
        model_name_or_class: type[models.Model],
    ) -> Recipe:
        return Recipe(
            model_name_or_class,
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
            PersonalInfo,
            first_name=self.faker.first_name,
            last_name=self.faker.last_name,
            email=self.faker.email,
            communication_language_mode=self.faker.random_element(CommunicationLanguageMode.values),
            telegram_username=self.faker.user_name,
            phone=self.faker.numerify("+3531#######"),
            information_source=self.faker.text,
            registration_telegram_bot_chat_id=self.faker.pyint,
            registration_telegram_bot_language=lambda: self.faker.random_element(
                RegistrationTelegramBotLanguage.values
            ),
            chatwoot_conversation_id=self.faker.pyint,
            utc_timedelta=lambda: timedelta(
                hours=self.faker.pyint(min_value=-12, max_value=12),
                minutes=self.faker.random_element([0, 30]),
            ),
        )

    def _make_coordinator_recipe(self) -> Recipe:
        return Recipe(
            Coordinator,
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            is_admin=self.faker.pybool,
            is_validated=self.faker.pybool,
            project_status=lambda: self.faker.random_element(CoordinatorProjectStatus.values),
        )

    def _make_student_recipe(self) -> Recipe:
        return Recipe(
            Student,
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            project_status=lambda: self.faker.random_element(StudentProjectStatus.values),
            age_range=lambda: self.faker.random_element(AgeRange.objects.filter(type=AgeRangeType.STUDENT) or [None]),
            availability_slots=lambda: self._get_random_amount_of_objects(DayAndTimeSlot, min_length=10, max_length=20),
            can_read_in_english=self.faker.pybool,
            is_member_of_speaking_club=self.faker.pybool,
            non_teaching_help_required=lambda: self._get_random_amount_of_objects(NonTeachingHelp),
            smalltalk_test_result=self.faker.json,
            teaching_languages_and_levels=lambda: self._get_random_amount_of_objects(LanguageAndLevel, max_length=2),
        )

    def _make_teacher_recipe(self) -> Recipe:
        return Recipe(
            Teacher,
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            project_status=lambda: self.faker.random_element(TeacherProjectStatus.values),
            can_host_speaking_club=self.faker.pybool,
            has_hosted_speaking_club=self.faker.pybool,
            is_validated=self.faker.pybool,
            availability_slots=lambda: self._get_random_amount_of_objects(DayAndTimeSlot, min_length=10, max_length=20),
            non_teaching_help_provided=lambda: self._get_random_amount_of_objects(NonTeachingHelp),
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
            teaching_languages_and_levels=lambda: self._get_random_amount_of_objects(LanguageAndLevel),
            weekly_frequency_per_group=self.faker.pyint,
        )

    def _make_teacher_under_18_recipe(self) -> Recipe:
        return Recipe(
            TeacherUnder18,
            personal_info=foreign_key(self.personal_info, one_to_one=True),
            comment=self.faker.text,
            project_status=lambda: self.faker.random_element(TeacherProjectStatus.values),
            can_host_speaking_club=self.faker.pybool,
            has_hosted_speaking_club=self.faker.pybool,
            is_validated=self.faker.pybool,
        )

    def _make_group_recipe(self) -> Recipe:
        group_common_recipe = self._make_group_common_recipe(Group)
        return group_common_recipe.extend(
            availability_slots_for_auto_matching=lambda: self._get_random_amount_of_objects(
                DayAndTimeSlot, min_length=10, max_length=20
            ),
            is_for_staff_only=self.faker.pybool,
            language_and_level=lambda: self.faker.random_element(LanguageAndLevel.objects.all() or [None]),
            lesson_duration_in_minutes=lambda: self.faker.pyint(min_value=30, max_value=120, step=30),
            project_status=lambda: self.faker.random_element(GroupProjectStatus.values),
            start_date=self.faker.past_date,
            end_date=self.faker.future_date,
            **self._get_group_days_of_week(),
        )

    def _make_speaking_club_recipe(self) -> Recipe:
        group_common_recipe = self._make_group_common_recipe(SpeakingClub)
        return group_common_recipe.extend(
            is_for_children=self.faker.pybool,
            language=lambda: self.faker.random_element(Language.objects.all() or [None]),
            teachers_under_18=lambda: related(
                *[self.teacher_under_18]
                * self.faker.pyint(
                    min_value=MIN_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB,
                    max_value=MAX_AMOUNT_OF_TEACHERS_UNDER_18_IN_SPEAKING_CLUB,
                )
            ),
        )


class FakeDataPopulator:
    def __init__(self) -> None:
        self.recipes = RecipeStorage()
        self.stdout = sys.stdout
        self.style: Any = None

    def _make_amount_of_recipe_and_skip_database_error(self, recipe: Recipe, amount: int) -> None:
        """
        Ensures that given amount of objects is made.
        While generating objects by recipe, it is possible that some of them will violate any db constraint.
        We need to recreate such objects to skip db constraints and be sure that needed amount is generated.
        """
        created_count = 0
        attempts = 0
        max_attempts_per_item = 10

        while created_count < amount:
            current_item_attempts = 0
            while True:
                if current_item_attempts >= max_attempts_per_item:
                    self.stdout.write(
                        f"Warning: Max attempts reached for one item of recipe {recipe._model.__name__}. \
                        Skipping this item. ({created_count}/{amount} created)"
                    )
                    break
                try:
                    with transaction.atomic():
                        recipe.make()
                        created_count += 1
                        self.stdout.write(
                            f"Successfully created item {created_count}/{amount} for {recipe._model.__name__}"
                        )
                        break
                except DatabaseError as e:
                    self.stdout.write(f"Error: {str(e)}. Regenerating fake data for {recipe._model.__name__}...")
                    current_item_attempts += 1
                    attempts += 1
            if current_item_attempts >= max_attempts_per_item and created_count < amount:
                pass
        self.stdout.write(
            f"Finished creating {created_count}/{amount} for {recipe._model.__name__} after {attempts} retries."
        )

    def _make_fake_coordinators_without_group(self) -> None:
        self.stdout.write("Making fake coordinators without group...")
        self._make_amount_of_recipe_and_skip_database_error(
            self.recipes.coordinator, AMOUNT_OF_COORDINATORS_WITHOUT_GROUP
        )

    def _make_fake_students_without_group(self) -> None:
        self.stdout.write("Making fake students without group...")
        self._make_amount_of_recipe_and_skip_database_error(self.recipes.student, AMOUNT_OF_STUDENTS_WITHOUT_GROUP)

    def _make_fake_teachers_without_group(self) -> None:
        self.stdout.write("Making fake teachers without groups...")
        self._make_amount_of_recipe_and_skip_database_error(self.recipes.teacher, AMOUNT_OF_TEACHERS_WITHOUT_GROUP)

    def _make_fake_teachers_under_18_without_speaking_club(self) -> None:
        self.stdout.write("Making fake teachers under 18 without speaking club...")
        self._make_amount_of_recipe_and_skip_database_error(
            self.recipes.teacher_under_18,
            AMOUNT_OF_TEACHERS_UNDER_18_WITHOUT_SPEAKING_CLUB,
        )

    def _make_fake_groups(self) -> None:
        self.stdout.write("Making fake groups...")
        self._make_amount_of_recipe_and_skip_database_error(self.recipes.group, AMOUNT_OF_GROUPS)

    def _make_fake_speaking_clubs(self) -> None:
        self.stdout.write("Making fake speaking clubs...")
        self._make_amount_of_recipe_and_skip_database_error(self.recipes.speaking_club, AMOUNT_OF_SPEAKING_CLUBS)

    def populate(self) -> None:
        """Runs operations required for populating the database with fake data."""
        self.stdout.write("Starting fake data population...")

        # data like AgeRange, DayAndTimeSlot, etc. must be
        # populated BEFORE running this command

        if not AgeRange.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Warning: No AgeRange objects found. Student/Teacher creation might fail or be limited."
                )
            )
        if not DayAndTimeSlot.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Warning: No DayAndTimeSlot objects found. Student/Teacher/Group creation might fail or be limited."
                )
            )
        if not Language.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Warning: No Language objects found. Speaking club creation might fail or be limited."
                )
            )
        if not LanguageAndLevel.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Warning: No LanguageAndLevel objects found. Student/Group creation might fail or be limited."
                )
            )

        self._make_fake_students_without_group()
        self._make_fake_coordinators_without_group()
        self._make_fake_teachers_without_group()
        self._make_fake_teachers_under_18_without_speaking_club()
        self._make_fake_groups()
        self._make_fake_speaking_clubs()
        self.stdout.write(self.style.SUCCESS("Fake data population complete!"))


class Command(BaseCommand):
    help = "Populates the database with fake data for development and testing."

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        populator = FakeDataPopulator()
        populator.stdout = self.stdout
        populator.style = self.style

        self.stdout.write(
            "Pre-requisite: Ensure that basic data from migration '0002_data_migration' \
              exists (AgeRanges, DayTimeSlots, Languages, etc.)."
        )

        if PersonalInfo.objects.exists():
            self.stdout.write(self.style.WARNING("Fake data seems to exist already (found PersonalInfo objects)."))
            if input("Do you want to add more fake data? (yes/no): ").lower() != "yes":
                self.stdout.write("Aborting.")
                return

        populator.populate()
