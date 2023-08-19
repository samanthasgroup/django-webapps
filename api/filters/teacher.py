from django_filters import rest_framework as filters

from api.models import Teacher


class TeacherFilter(filters.FilterSet):
    for_coordinator_email = filters.CharFilter(
        field_name="groups__coordinators__personal_info__email", lookup_expr="iexact"
    )

    class Meta:
        model = Teacher
        fields = (
            "for_coordinator_email",
            "project_status",
        )
