import pytest
from rest_framework import status

from api.models.age_range import AgeRange, AgeRangeType
from api.serializers import AgeRangeSerializer
from tests.tests_api.asserts import assert_response_data, assert_response_data_list


@pytest.mark.parametrize(
    "age_range_type",
    [AgeRangeType.STUDENT, AgeRangeType.TEACHER, AgeRangeType.MATCHING, None],
)
def test_age_range_list(api_client, age_range_type):
    queryset = AgeRange.objects.order_by("id")
    if age_range_type:
        queryset = queryset.filter(type=age_range_type)
        query_string = f"?type={age_range_type}"
    else:
        query_string = ""
    response = api_client.get(f"/api/age_ranges/{query_string}")

    assert response.status_code == status.HTTP_200_OK
    assert_response_data_list(
        response.data, [AgeRangeSerializer(age_range).data for age_range in queryset]
    )


def test_age_range_retrieve(api_client):
    age_range = AgeRange.objects.first()
    response = api_client.get(f"/api/age_ranges/{age_range.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, AgeRangeSerializer(age_range).data)
