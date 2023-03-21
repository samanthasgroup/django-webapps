from rest_framework import serializers

from api.models import TeacherUnder18


class TeacherUnder18Serializer(serializers.ModelSerializer[TeacherUnder18]):
    class Meta:
        model = TeacherUnder18
        fields = "__all__"
