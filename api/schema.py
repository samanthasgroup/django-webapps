from drf_spectacular.openapi import AutoSchema
from rest_framework.permissions import SAFE_METHODS

from api.serializers.errors import ValidationErrorSerializer


class CustomSchema(AutoSchema):
    """
    Differences from default schema:
    - Default schema uses same tag (from url) for all endpoints.
      To make it more clear, we use viewset name as additional tag.
    - We add 400 response for all endpoints with unsafe method.
      (Also some other responses can be added here in the future, such as 403 etc.).
    """

    def get_tags(self) -> list[str]:
        tags = super().get_tags()
        view_set_tag_name = self.view.__class__.__name__.replace("ViewSet", "")
        return tags + [view_set_tag_name]

    def _get_response_bodies(self, direction="response"):
        bodies = super()._get_response_bodies(direction)
        if self.method not in SAFE_METHODS and direction == "response":
            bodies["400"] = self._get_response_for_code(
                serializer=ValidationErrorSerializer,
                status_code="400",
            )
        return bodies
