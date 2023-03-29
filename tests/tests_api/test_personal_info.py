"""
We are testing only `create`, `update`, `check_existence` actions,
because other actions are not supposed to be used.

TODO:
 Maybe we should remove some actions from ViewSet?
 Needs to be discussed for all viewsets.
"""

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


def test_personal_info_check_existence_returns_400_with_existing_info(api_client):
    existing_personal_info = baker.make(PersonalInfo)
    response = api_client.post(
        "/api/personal_info/check_existence/",
        data={
            "email": existing_personal_info.email,
            "first_name": existing_personal_info.first_name,
            "last_name": existing_personal_info.last_name,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"non_field_errors": ["User with this information already exists."]}
