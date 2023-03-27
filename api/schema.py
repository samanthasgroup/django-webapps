from typing import Any

from drf_spectacular.openapi import AutoSchema
from rest_framework.permissions import SAFE_METHODS

from api.serializers.errors import ValidationErrorSerializer


class CustomSchema(AutoSchema):
    """
    Custom schema for drf-spectacular.

    Differences from default schema:
    - Default schema uses same tag - first non-parameter path part as tag for all endpoints.
      (e.g. /api/users/ -> tag: api and also /api/other/ -> tag: api).
      To make it more clear, we override the get_tags() method to include viewset name as additional tag.
    - We add 400 response for all endpoints with unsafe method.
      (Also some other responses can be added here in the future, such as 403 etc.).
    """

    def get_tags(self) -> list[str]:
        tags = super().get_tags()
        view_set_tag_name = self.view.__class__.__name__.replace("ViewSet", "")
        return tags + [view_set_tag_name]

    def _get_response_bodies(self, direction: str = "response") -> dict[str, Any]:
        bodies = super()._get_response_bodies(direction)
        if self.method not in SAFE_METHODS and direction == "response":
            bodies["400"] = self._get_response_for_code(
                serializer=ValidationErrorSerializer,
                status_code="400",
            )
        return bodies
