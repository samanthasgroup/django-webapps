import pytest
from rest_framework import status

from api.models.age_ranges import AgeRange, AgeRangeType


@pytest.mark.parametrize(
    "age_range_type",
    [AgeRangeType.STUDENT, AgeRangeType.TEACHER, AgeRangeType.MATCHING, None],
)
def test_age_range_list(admin_client, age_range_type):
    queryset = AgeRange.objects.order_by("id")
    if age_range_type:
        queryset = queryset.filter(type=age_range_type)
        query_string = f"?type={age_range_type}"
    else:
        query_string = ""
    response = admin_client.get(f"/api/age_ranges/{query_string}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": age_range.id,
            "age_from": age_range.age_from,
            "age_to": age_range.age_to,
            "type": age_range.type,
        }
        for age_range in queryset
    ]


def test_age_range_retrieve(admin_client):
    age_range = AgeRange.objects.first()
    response = admin_client.get(f"/api/age_ranges/{age_range.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": age_range.id,
        "age_from": age_range.age_from,
        "age_to": age_range.age_to,
        "type": age_range.type,
    }
