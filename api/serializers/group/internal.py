from typing import Any

from django.utils import timezone
from rest_framework import serializers

from api.exceptions import ConflictError
from api.models import Group
from api.models.auxil.constants import GroupDiscardReason
from api.models.choices.status import GroupProjectStatus
from api.serializers import (
    DayAndTimeSlotSerializer,
    MinifiedStudentSerializer,
    MinifiedTeacherSerializer,
    coordinator,
)


class GroupWriteSerializer(serializers.ModelSerializer[Group]):
    status_since = serializers.DateTimeField(default=timezone.now())
    project_status = serializers.ChoiceField(GroupProjectStatus, default=GroupProjectStatus.PENDING)

    class Meta:
        model = Group
        fields = "__all__"


class GroupReadSerializer(serializers.ModelSerializer[Group]):
    availability_slots_for_auto_matching = DayAndTimeSlotSerializer(many=True, read_only=True)
    coordinators = coordinator.MinifiedCoordinatorSerializer(many=True, read_only=True)
    students = MinifiedStudentSerializer(many=True, read_only=True)
    teachers = MinifiedTeacherSerializer(
        many=True,
        read_only=True,
    )
    coordinators_former = coordinator.MinifiedCoordinatorSerializer(many=True, read_only=True, required=False)
    students_former = MinifiedStudentSerializer(many=True, read_only=True, required=False)
    teachers_former = MinifiedTeacherSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Group
        fields = "__all__"


class GroupDiscardSerializer(serializers.Serializer[Any]):
    discard_reason = serializers.ChoiceField(choices=[e.value for e in GroupDiscardReason])

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if self.instance is not None and self.instance.project_status != GroupProjectStatus.PENDING:
            raise ConflictError("Group is not in the pending state")
        return attrs
