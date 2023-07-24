from rest_framework import status

from api.models import DayAndTimeSlot
from api.serializers import DayAndTimeSlotSerializer
from tests.tests_api.asserts import assert_response_data, assert_response_data_list


def test_day_and_time_slot_list(api_client):
    queryset = DayAndTimeSlot.objects.all()
    response = api_client.get("/api/day_and_time_slots/")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data_list(
        response.data,
        [DayAndTimeSlotSerializer(day_and_time_slot).data for day_and_time_slot in queryset],
    )


def test_day_and_time_slots_retrieve(api_client):
    day_and_time_slot = DayAndTimeSlot.objects.first()
    response = api_client.get(f"/api/day_and_time_slots/{day_and_time_slot.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, DayAndTimeSlotSerializer(day_and_time_slot).data)
