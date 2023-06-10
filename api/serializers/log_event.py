from rest_framework import serializers

from api.models import (
    CoordinatorLogEvent,
    GroupLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
    TeacherUnder18LogEvent,
)
from api.serializers import MinifiedStudentSerializer, TeacherUnder18ReadSerializer
from api.serializers.coordinator import MinifiedCoordinatorSerializer
from api.serializers.group.minified import MinifiedGroupSerializer
from api.serializers.teacher.minified import MinifiedTeacherSerializer


class CoordinatorLogEventReadSerializer(serializers.ModelSerializer[CoordinatorLogEvent]):
    """A serializer for reading coordinator's log events."""

    coordinator = MinifiedCoordinatorSerializer(read_only=True)

    from_group = MinifiedGroupSerializer(read_only=True)
    to_group = MinifiedGroupSerializer(read_only=True)

    class Meta:
        model = CoordinatorLogEvent
        fields = ("coordinator", "date_time", "type", "from_group", "to_group", "comment")


class CoordinatorLogEventWriteSerializer(serializers.ModelSerializer[CoordinatorLogEvent]):
    """A serializer for writing coordinator's log events."""

    coordinator_id = serializers.IntegerField()
    group_id = serializers.IntegerField()

    class Meta:
        model = CoordinatorLogEvent
        fields = ("type", "coordinator_id", "group_id", "comment")
        extra_kwargs = {"coordinator_id": {"required": True}}


class GroupLogEventReadSerializer(serializers.ModelSerializer[GroupLogEvent]):
    """A serializer for reading group's log events."""

    group = MinifiedGroupSerializer(read_only=True)

    class Meta:
        model = GroupLogEvent
        fields = ("group", "date_time", "type", "comment")
        extra_kwargs = {"group_id": {"required": True}}


class GroupLogEventWriteSerializer(serializers.ModelSerializer[GroupLogEvent]):
    """A serializer for writing group's log events."""

    group_id = serializers.IntegerField()

    class Meta:
        model = GroupLogEvent
        fields = ("type", "group_id", "comment")


class StudentLogEventReadSerializer(serializers.ModelSerializer[StudentLogEvent]):
    """A serializer for reading student's log events."""

    student = MinifiedStudentSerializer(read_only=True)

    from_group = MinifiedGroupSerializer(read_only=True)
    to_group = MinifiedGroupSerializer(read_only=True)

    class Meta:
        model = StudentLogEvent
        fields = ("student", "date_time", "type", "from_group", "to_group", "comment")


class StudentLogEventWriteSerializer(serializers.ModelSerializer[StudentLogEvent]):
    """A serializer for writing student's log events."""

    student_id = serializers.IntegerField()
    to_group_id = serializers.IntegerField()
    from_group_id = serializers.IntegerField()

    class Meta:
        model = StudentLogEvent
        fields = ("type", "student_id", "from_group_id", "to_group_id", "comment")
        extra_kwargs = {"student_id": {"required": True}}


class TeacherLogEventReadSerializer(serializers.ModelSerializer[TeacherLogEvent]):
    """A serializer for reading adult teacher's log events."""

    teacher = MinifiedTeacherSerializer(read_only=True)

    from_group = MinifiedGroupSerializer(read_only=True)
    to_group = MinifiedGroupSerializer(read_only=True)

    class Meta:
        model = TeacherLogEvent
        fields = ("teacher", "date_time", "type", "from_group", "to_group", "comment")


class TeacherLogEventWriteSerializer(serializers.ModelSerializer[TeacherLogEvent]):
    """A serializer for writing adult teacher's log events."""

    teacher_id = serializers.IntegerField()
    to_group_id = serializers.IntegerField()
    from_group_id = serializers.IntegerField()

    class Meta:
        model = TeacherLogEvent
        fields = ("type", "teacher_id", "from_group_id", "to_group_id", "comment")
        extra_kwargs = {"teacher_id": {"required": True}}


class TeacherUnder18LogEventReadSerializer(serializers.ModelSerializer[TeacherUnder18LogEvent]):
    """A serializer for reading young teacher's log events."""

    teacher = TeacherUnder18ReadSerializer(read_only=True)

    class Meta:
        model = TeacherUnder18LogEvent
        fields = ("teacher", "date_time", "type", "comment")


class TeacherUnder18LogEventWriteSerializer(serializers.ModelSerializer[TeacherUnder18LogEvent]):
    """A serializer for writing young teacher's log events."""

    teacher_id = serializers.IntegerField()

    class Meta:
        model = TeacherUnder18LogEvent
        fields = ("type", "teacher_id", "comment")
        extra_kwargs = {"teacher_id": {"required": True}}
