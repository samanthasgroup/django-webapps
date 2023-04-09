from rest_framework import serializers

from api.models import NonTeachingHelp


class NonTeachingHelpSerializer(serializers.ModelSerializer[NonTeachingHelp]):
    class Meta:
        model = NonTeachingHelp
        fields = "__all__"
