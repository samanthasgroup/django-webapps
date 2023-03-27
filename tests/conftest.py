import pytest
from rest_framework.test import APIClient

from api.models import PersonalInfo


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
    pass


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    """
    A pytest fixture that returns the locale for Faker.
    """
    return ["ru_RU"]


@pytest.fixture
def fake_personal_info_data(faker):
    return {
        "communication_language_mode": faker.random_element(
            PersonalInfo.CommunicationLanguageMode.values
        ),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "tg_username": faker.user_name(),
        "email": faker.email(),
        "phone": faker.numerify("+791########"),
        "utc_timedelta": "03:00:00",
        "information_source": faker.pystr(),
        "registration_bot_chat_id": faker.pyint(),
        "registration_bot_language": faker.random_element(
            PersonalInfo.RegistrationBotLanguage.values
        ),
        "chatwoot_conversation_id": faker.pyint(),
    }
