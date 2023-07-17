from typing import Any

from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import Group
from api.processors import GroupProcessor


class CreateGroupMixin(CreateModelMixin):
    """Mixin for group creation. Shared between dashboard and internal router"""

    def create(self, request: Request, *args: tuple[Any], **kwargs: dict[str, Any]) -> Response:
        response = super().create(request, *args, **kwargs)
        group = Group.objects.get(id=response.data["id"])
        GroupProcessor.create(group)
        return response
