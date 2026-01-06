import pytest

from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage


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
        "registration_telegram_bot_language": faker.random_element(RegistrationTelegramBotLanguage.values),
        "chatwoot_conversation_id": faker.pyint(),
    }


@pytest.fixture
def fake_personal_info_list(faker):
    return [
        {
            "communication_language_mode": faker.random_element(CommunicationLanguageMode.values),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "telegram_username": faker.user_name(),
            "email": faker.email(),
            "phone": faker.numerify("+3531#######"),
            "utc_timedelta": "03:00:00",
            "information_source": faker.text(),
            "registration_telegram_bot_chat_id": faker.pyint(),
            "registration_telegram_bot_language": faker.random_element(RegistrationTelegramBotLanguage.values),
            "chatwoot_conversation_id": faker.pyint(),
        }
        for _ in range(10)
    ]
