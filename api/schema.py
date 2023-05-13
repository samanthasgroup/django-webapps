from typing import Any, Literal

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import build_basic_type, build_object_type
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import SAFE_METHODS

from api.models.choices.non_teaching_help import NonTeachingHelpType
from api.models.constants import TEACHER_PEER_SUPPORT_OPTIONS
from api.serializers.errors import ValidationErrorSerializer


class CustomSchema(AutoSchema):
    """
    Custom schema for drf-spectacular.

    Differences from default schema:
    - Default schema uses same tag - first non-parameter path part as tag for all endpoints.
      (e.g. /api/users/ -> tag: api and also /api/other/ -> tag: api).
      To make it more clear, we override the get_tags() method
      to include viewset name as additional tag.
    - We override _get_response_bodies() method to add 400 response
      for all requests to endpoints with unsafe methods.
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


class TeacherNonTeachingHelpProvidedFieldFix(OpenApiSerializerFieldExtension):
    """
    This class automatically extends schema for NonTeachingHelpPublicSerializerField,
    showing this object properly in docs.
    """

    target_class = "api.serializers.non_teaching_help.NonTeachingHelpPublicSerializerField"

    def map_serializer_field(
        self, auto_schema: AutoSchema, direction: Literal["request", "response"]  # noqa: ARG002
    ) -> dict[str, Any]:
        return build_object_type(
            properties={
                option: build_basic_type(OpenApiTypes.BOOL)
                for option in NonTeachingHelpType.values
            }
        )


class TeacherPeerSupportFieldFix(OpenApiSerializerFieldExtension):
    """
    This class automatically extends schema for NonTeachingHelpPublicSerializerField,
    showing this object properly in docs.
    """

    target_class = "api.serializers.teacher.PeerSupportField"

    def map_serializer_field(
        self, auto_schema: AutoSchema, direction: Literal["request", "response"]  # noqa: ARG002
    ) -> dict[str, Any]:
        return build_object_type(
            properties={
                option: build_basic_type(OpenApiTypes.BOOL)
                for option in TEACHER_PEER_SUPPORT_OPTIONS
            }
        )
