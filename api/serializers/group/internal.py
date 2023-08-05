from django.utils import timezone
from rest_framework import serializers

from api.models import Group
from api.models.choices.status import GroupProjectStatus
from api.serializers import (
    DayAndTimeSlotSerializer,
    MinifiedStudentSerializer,
    MinifiedTeacherSerializer,
    coordinator,
)


class GroupWriteSerializer(serializers.ModelSerializer[Group]):
    status_since = serializers.DateTimeField(default=timezone.now())
    status = serializers.ChoiceField(GroupProjectStatus, default=GroupProjectStatus.PENDING)

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
    coordinators_former = coordinator.MinifiedCoordinatorSerializer(
        many=True, read_only=True, required=False
    )
    students_former = MinifiedStudentSerializer(many=True, read_only=True, required=False)
    teachers_former = MinifiedTeacherSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Group
        fields = "__all__"
