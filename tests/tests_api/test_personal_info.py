"""
We are testing only `create`, `update`, `check_existence` actions,
because other actions are not supposed to be used.

TODO:
 Maybe we should remove some actions from ViewSet?
 Needs to be discussed for all viewsets.
"""
import pytest
from django.utils.dateparse import parse_duration
from model_bakery import baker
from rest_framework import status

from api.models import PersonalInfo


def test_personal_info_create(api_client, fake_personal_info_data):
    initial_count = PersonalInfo.objects.count()
    response = api_client.post("/api/personal_info/", data=fake_personal_info_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert PersonalInfo.objects.count() == initial_count + 1

    # Changing it to a timedelta object for further filtering
    fake_personal_info_data["utc_timedelta"] = parse_duration(
        fake_personal_info_data["utc_timedelta"]
    )

    assert PersonalInfo.objects.filter(**fake_personal_info_data).exists()


def test_personal_info_update(api_client, fake_personal_info_data):
    personal_info = baker.make(PersonalInfo)
    initial_count = PersonalInfo.objects.count()

    response = api_client.put(
        f"/api/personal_info/{personal_info.id}/", data=fake_personal_info_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert PersonalInfo.objects.count() == initial_count

    # Changing it to a timedelta object for further filtering
    fake_personal_info_data["utc_timedelta"] = parse_duration(
        fake_personal_info_data["utc_timedelta"]
    )

    assert PersonalInfo.objects.filter(**fake_personal_info_data).exists()


def test_personal_info_check_existence_returns_409_with_existing_info(api_client):
    existing_personal_info = baker.make(PersonalInfo)
    response = api_client.post(
        "/api/personal_info/check_existence/",
        data={
            "email": existing_personal_info.email,
            "first_name": existing_personal_info.first_name,
            "last_name": existing_personal_info.last_name,
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Object with this data already exists."}


@pytest.mark.parametrize(
    "email", ["test", "test@", "test@test", "test@test.", "test@test.c", "емейл", "емейл@ру.ру"]
)
def test_personal_info_check_existence_returns_400_with_invalid_email(api_client, email, faker):
    response = api_client.post(
        "/api/personal_info/check_existence/",
        data={
            "email": email,
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"email": ["Enter a valid email address."]}


def test_personal_info_check_existence_of_chat_id_returns_200_with_existing_id(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    response = api_client.get(
        path="/api/personal_info/check_existence_of_chat_id/",
        data={
            "registration_telegram_bot_chat_id": fake_personal_info_data[
                "registration_telegram_bot_chat_id"
            ]
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_personal_info_check_existence_of_chat_id_returns_406_with_unknown_id(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    response = api_client.get(
        path="/api/personal_info/check_existence_of_chat_id/",
        data={
            "registration_telegram_bot_chat_id": fake_personal_info_data[
                "registration_telegram_bot_chat_id"
            ]
            + 1
        },
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() == {"detail": "No object with this data exists."}


def test_personal_info_check_existence_of_chat_id_returns_400_with_no_id_passed(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    response = api_client.get(path="/api/personal_info/check_existence_of_chat_id/", data={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"registration_telegram_bot_chat_id": ["This field is required."]}


def test_personal_info_check_existence_of_chat_id_returns_400_with_no_id(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    response = api_client.get(
        path="/api/personal_info/check_existence_of_chat_id/",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"registration_telegram_bot_chat_id": ["This field is required."]}
