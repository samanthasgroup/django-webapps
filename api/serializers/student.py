from rest_framework import serializers

from api.models import Student


class StudentSerializer(serializers.ModelSerializer):
    # TODO Here and in other serializers, we should decide,
    #  which id we use for linking with PersonalInfo - uuid or id
    class Meta:
        model = Student
        fields = "__all__"
