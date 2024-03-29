import pytest
from rest_framework import status

from api.models import DayAndTimeSlot


@pytest.mark.parametrize("base_route", ["api", "api/dashboard"])
def test_day_and_time_slot_list(api_client, base_route):
    queryset = DayAndTimeSlot.objects.all()
    response = api_client.get(f"/{base_route}/day_and_time_slots/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": day_and_time_slot.id,
            "time_slot": {
                "id": day_and_time_slot.time_slot.id,
                # Since these fields are TimeFields, they are returned as strings
                "from_utc_hour": str(day_and_time_slot.time_slot.from_utc_hour),
                "to_utc_hour": str(day_and_time_slot.time_slot.to_utc_hour),
            },
            "day_of_week_index": day_and_time_slot.day_of_week_index,
        }
        for day_and_time_slot in queryset
    ]


@pytest.mark.parametrize("base_route", ["api", "api/dashboard"])
def test_day_and_time_slots_retrieve(api_client, base_route):
    day_and_time_slot = DayAndTimeSlot.objects.first()
    response = api_client.get(f"/{base_route}/day_and_time_slots/{day_and_time_slot.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": day_and_time_slot.id,
        "time_slot": {
            "id": day_and_time_slot.time_slot.id,
            # Since these fields are TimeFields, they are returned as strings
            "from_utc_hour": str(day_and_time_slot.time_slot.from_utc_hour),
            "to_utc_hour": str(day_and_time_slot.time_slot.to_utc_hour),
        },
        "day_of_week_index": day_and_time_slot.day_of_week_index,
    }
