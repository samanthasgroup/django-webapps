from rest_framework import serializers

from api.models import people


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = people.PersonalInfo
        fields = "__all__"
