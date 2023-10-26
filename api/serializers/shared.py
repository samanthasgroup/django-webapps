from typing import Any

from rest_framework import serializers

from api.exceptions import UnproccessableEntityError
from api.models import Group


class PersonTransferSerializer(serializers.Serializer[Any]):
    to_group_id = serializers.IntegerField()
    from_group_id = serializers.IntegerField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            to_group = Group.objects.get(pk=int(attrs["to_group_id"]))
        except Group.DoesNotExist:
            raise UnproccessableEntityError(f"Group {attrs['to_group_id']} not found")

        attrs["to_group"] = to_group

        try:
            from_group = Group.objects.get(pk=int(attrs["from_group_id"]))
        except Group.DoesNotExist:
            raise UnproccessableEntityError(f"Group {attrs['from_group_id']} not found")
        attrs["from_group"] = from_group

        return attrs
