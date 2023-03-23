import pytest


@pytest.fixture
def api_client(client):
    """
    A pytest fixture that returns an API client.
    """
    # Now using default client because we don't have any API permissions
    return client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(
    db,  # noqa  ruff states db param as unused, but it's used as a fixture
):
    """
    A pytest fixture that enables database access for all tests.
    """
    pass
