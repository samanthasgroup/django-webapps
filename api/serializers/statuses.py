from rest_framework import serializers

from api.models.statuses import StudentStatus, StudentStatusName, TeacherStatus, TeacherStatusName


class StudentStatusNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatusName
        fields = ["name"]


class TeacherStatusNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherStatusName
        fields = ["name"]


class StudentStatusSerializer(serializers.ModelSerializer):
    name = StudentStatusNameSerializer()

    class Meta:
        model = StudentStatus
        fields = ["name"]


class TeacherStatusSerializer(serializers.ModelSerializer):
    name = TeacherStatusNameSerializer()

    class Meta:
        model = TeacherStatus
        fields = ["name"]
