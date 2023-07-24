import datetime


def assert_response_data(response_data: dict, fields_to_assert: dict) -> None:
    """
    Does assertion of response data fields specified in fields_to_assert
    """
    for field, val in fields_to_assert.items():
        assert val == response_data[field]


def assert_response_data_list(
    response_data_items: list[dict], data_items_to_assert: list[dict]
) -> None:
    """
    Does assertion of every response data list item with corresponding item specified
    in data_items_to_assert

    Note:
        both parameters have to have equal lengths
    """
    assert len(response_data_items) == len(data_items_to_assert)
    for response_data, data_to_assert in zip(response_data_items, data_items_to_assert):
        assert_response_data(response_data, data_to_assert)


def assert_date_time_with_timestamp(date_time: datetime.datetime, timestamp: datetime.datetime):
    """Compares the given datetime object with timestamp from conftest.py.

    Allows for a one-minute margin between timestamp and the datetime being checked.

    Used e.g. to compare `status_since` attribute after status change.

    For this test to be informative, make sure you manually set status_since to
    some date in the past so that the match with timestamp after status change is not accidental.
    """
    assert date_time - timestamp < datetime.timedelta(minutes=1)
