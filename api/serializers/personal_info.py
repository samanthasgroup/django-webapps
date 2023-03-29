from typing import Any

from rest_framework import serializers

from api.models import PersonalInfo


class PersonalInfoSerializer(serializers.ModelSerializer[PersonalInfo]):
    class Meta:
        model = PersonalInfo
        fields = "__all__"


class PersonalInfoCheckExistenceSerializer(serializers.ModelSerializer[PersonalInfo]):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if PersonalInfo.objects.filter(**attrs).exists():
            # TODO: Discuss errors format.
            raise serializers.ValidationError("User with this information already exists.")
        return attrs

    class Meta:
        model = PersonalInfo
        fields = ["first_name", "last_name", "email"]
