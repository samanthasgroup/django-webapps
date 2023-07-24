import pytest

from api.models import DayAndTimeSlot


@pytest.fixture(scope="session")
def availability_slots():
    """
    Use where `DayAndTimeSlot`s with unique constraints are involved, so as to avoid random errors.

    Note:
        For some cases you might need random set of slots, in that case use different fixture.
    """
    return DayAndTimeSlot.objects.all()
