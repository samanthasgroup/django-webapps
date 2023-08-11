import pytest
from django.utils import timezone
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """
    A pytest fixture that returns an API client.
    """
    # Now using default client because we don't have any API permissions
    return APIClient()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(
    db,  # noqa  ruff states db param as unused, but it's used as a fixture
):
    """
    A pytest fixture that enables database access for all tests.
    """


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    """
    A pytest fixture that returns the locale for Faker.
    """
    return ["ru_RU"]


@pytest.fixture(scope="module")
def timestamp():
    yield timezone.now()
