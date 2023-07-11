import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import DayAndTimeSlot
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage


@pytest.fixture
def api_client():
    """
    A pytest fixture that returns an API client.
    """
    # Now using default client because we don't have any API permissions
    return APIClient()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(
    db,  # noqa  ruff states db param as unused, but it's used as a fixture
):
    """
    A pytest fixture that enables database access for all tests.
    """


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    """
    A pytest fixture that returns the locale for Faker.
    """
    return ["ru_RU"]


@pytest.fixture
def fake_personal_info_data(faker):
    return {
        "communication_language_mode": faker.random_element(CommunicationLanguageMode.values),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "telegram_username": faker.user_name(),
        "email": faker.email(),
        "phone": faker.numerify("+3531#######"),
        "utc_timedelta": "03:00:00",
        "information_source": faker.text(),
        "registration_telegram_bot_chat_id": faker.pyint(),
        "registration_telegram_bot_language": faker.random_element(
            RegistrationTelegramBotLanguage.values
        ),
        "chatwoot_conversation_id": faker.pyint(),
    }


@pytest.fixture(scope="module")
def timestamp():
    yield timezone.now()


@pytest.fixture(scope="session")
def availability_slots():
    """
    Use where `DayAndTimeSlot`s with unique constraints are involved, so as to avoid random errors.

    Note:
        For some cases you might need random set of slots, in that case use different fixture.
    """
    return DayAndTimeSlot.objects.all()


pytest_plugins = [
    "tests.fixtures.group",
]
