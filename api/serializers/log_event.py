from rest_framework import serializers

from api.models import (
    CoordinatorLogEvent,
    GroupLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
    TeacherUnder18LogEvent,
)


class CoordinatorLogEventSerializer(serializers.ModelSerializer[CoordinatorLogEvent]):
    """A serializer for coordinator's log events."""

    coordinator_id = serializers.IntegerField(source="coordinator_id", required=True)

    from_group_id = serializers.IntegerField(source="from_group_id")
    to_group_id = serializers.IntegerField(source="to_group_id")

    class Meta:
        model = CoordinatorLogEvent
        fields = ("date_time", "type", "coordinator_id", "from_group_id", "to_group_id", "comment")


class GroupLogEventSerializer(serializers.ModelSerializer[GroupLogEvent]):
    """A serializer for group's log events."""

    group_id = serializers.IntegerField(source="group_id", required=True)

    class Meta:
        model = GroupLogEvent
        fields = ("date_time", "type", "group_id", "comment")


class StudentLogEventSerializer(serializers.ModelSerializer[StudentLogEvent]):
    """A serializer for student's log events."""

    student_id = serializers.IntegerField(source="student_id", required=True)

    from_group_id = serializers.IntegerField(source="from_group_id")
    to_group_id = serializers.IntegerField(source="to_group_id")

    class Meta:
        model = StudentLogEvent
        fields = ("date_time", "type", "student_id", "from_group_id", "to_group_id", "comment")


class TeacherLogEventSerializer(serializers.ModelSerializer[TeacherLogEvent]):
    """A serializer for adult teacher's log events."""

    teacher_id = serializers.IntegerField(source="teacher_id", required=True)

    from_group_id = serializers.IntegerField(source="from_group_id")
    to_group_id = serializers.IntegerField(source="to_group_id")

    class Meta:
        model = TeacherLogEvent
        fields = ("date_time", "type", "teacher_id", "from_group_id", "to_group_id", "comment")


class TeacherUnder18LogEventSerializer(serializers.ModelSerializer[TeacherUnder18LogEvent]):
    """A serializer for young teacher's log events."""

    teacher_id = serializers.IntegerField(source="teacher_id", required=True)

    class Meta:
        model = TeacherUnder18LogEvent
        fields = ("date_time", "type", "teacher_id", "comment")
