from django_filters import rest_framework as filters

from api.models import Student


class StudentFilter(filters.FilterSet):
    for_coordinator_email = filters.CharFilter(
        field_name="groups__coordinators__personal_info__email", lookup_expr="iexact"
    )

    class Meta:
        model = Student
        fields = ("for_coordinator_email",)
