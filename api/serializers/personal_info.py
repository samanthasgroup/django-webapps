from rest_framework import serializers

from api.models import PersonalInfo


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = '__all__'
