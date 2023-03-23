from rest_framework import status


def test_docs_availability(api_client):
    """Smoke test for docs availability."""
    response = api_client.get("/docs/yaml-schema/")
    assert response.status_code == status.HTTP_200_OK
