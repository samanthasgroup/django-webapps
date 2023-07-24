import pytest
from rest_framework import status

from api.models import LanguageAndLevel
from api.serializers import LanguageAndLevelSerializer
from tests.tests_api.asserts import assert_response_data, assert_response_data_list


@pytest.mark.parametrize("language", [None, "en", "fr"])
def test_languages_and_levels_list(api_client, language):
    queryset = LanguageAndLevel.objects.all()

    if language:
        queryset = queryset.filter(language=language)
        query_string = f"?language={language}"
    else:
        query_string = ""

    response = api_client.get(f"/api/languages_and_levels/{query_string}")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data_list(
        response.data,
        [LanguageAndLevelSerializer(language_and_level).data for language_and_level in queryset],
    )


def test_languages_and_levels_retrieve(api_client):
    language_and_level = LanguageAndLevel.objects.first()
    response = api_client.get(f"/api/languages_and_levels/{language_and_level.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, LanguageAndLevelSerializer(language_and_level).data)
