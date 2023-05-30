from django_filters import rest_framework as filters

from api.models import Group


class GroupFilter(filters.FilterSet):
    for_coordinator_email = filters.CharFilter(
        field_name="coordinators__personal_info__email", lookup_expr="iexact"
    )

    class Meta:
        model = Group
        fields = ("for_coordinator_email",)
