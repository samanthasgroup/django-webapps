"""
We are testing only `create`, `update`, `check_existence` actions,
because other actions are not supposed to be used.

TODO:
 Maybe we should remove some actions from ViewSet?
 Needs to be discussed for all viewsets.
"""

import pytest
from django.utils.dateparse import parse_duration
from model_bakery import baker, seq
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


def test_personal_info_get_with_params_returns_200_and_data_with_existing_chat_id(
    api_client, fake_personal_info_data, fake_personal_info_list
):
    for item in fake_personal_info_list:
        api_client.post("/api/personal_info/", data=item)

    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    expected_chat_id = fake_personal_info_data["registration_telegram_bot_chat_id"]

    response = api_client.get(
        path=f"/api/personal_info/?registration_telegram_bot_chat_id={expected_chat_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    # checking some basic attrs (cannot compare two objects directly
    # because some fields were added during creation)
    for param in ["first_name", "last_name", "email", "information_source"]:
        assert response.json()[0][param] == fake_personal_info_data[param]


def test_dashboard_personal_info_get_applies_email_filter(
    api_client, fake_personal_info_data, fake_personal_info_list
):
    for item in fake_personal_info_list:
        api_client.post("/api/personal_info/", data=item)

    expected_id = api_client.post("/api/personal_info/", data=fake_personal_info_data).json()["id"]
    expected_email = fake_personal_info_data["email"]

    response = api_client.get(
        path="/api/dashboard/personal_info/",
        data={
            "email": expected_email,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    result = response.json()[0]
    assert result["id"] == expected_id
    assert result["email"] == expected_email


def test_dashboard_personal_info_get_handles_unknown_email(api_client, fake_personal_info_list):
    for item in fake_personal_info_list:
        api_client.post("/api/personal_info/", data=item)

    response = api_client.get(
        path="/api/dashboard/personal_info/",
        data={
            "email": "unknownEmail@samanthasgroup.com",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_personal_info_get_with_params_returns_200_and_empty_list_with_unknown_chat_id(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    non_existent_chat_id = fake_personal_info_data["registration_telegram_bot_chat_id"] + 1
    response = api_client.get(
        path=f"/api/personal_info/?registration_telegram_bot_chat_id={non_existent_chat_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_personal_info_update(api_client, fake_personal_info_data):
    # seq is used here to resolve compound unique constraint
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
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
    existing_personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
    response = api_client.post(
        "/api/personal_info/check_existence/",
        data={
            "email": existing_personal_info.email,
            "first_name": existing_personal_info.first_name,
            "last_name": existing_personal_info.last_name,
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "Personal info already exists"}


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
    assert "email" in response.json()
    assert isinstance(response.json()["email"], list)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


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


def test_personal_info_check_existence_of_chat_id_returns_400_with_no_id(
    api_client, fake_personal_info_data
):
    api_client.post("/api/personal_info/", data=fake_personal_info_data)
    response = api_client.get(path="/api/personal_info/check_existence_of_chat_id/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert "registration_telegram_bot_chat_id" in json_data
    assert isinstance(json_data["registration_telegram_bot_chat_id"], list)
