from django.db.models import QuerySet
from rest_framework import serializers

from api.models import NonTeachingHelp, Teacher
from api.models.choices.non_teaching_help import NonTeachingHelpType


class NonTeachingHelpSerializer(serializers.ModelSerializer[NonTeachingHelp]):
    class Meta:
        model = NonTeachingHelp
        fields = "__all__"


class NonTeachingHelpPublicSerializerField(serializers.Field):  # type: ignore
    """
    Representation of all possible NonTeachingHelp values for teacher
    that is used in 'All teachers' Tooljet view.
    """

    def to_representation(self, value: QuerySet[NonTeachingHelp]) -> dict[str, bool]:
        teacher_non_teaching_help_ids = set(value.all().values_list("id", flat=True))
        return {
            non_teaching_help_option: non_teaching_help_option in teacher_non_teaching_help_ids
            for non_teaching_help_option in NonTeachingHelpType.values
        }

    class Meta:
        model = Teacher
        fields = NonTeachingHelpType.values
