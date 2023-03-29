from django_filters import rest_framework as filters

from api.models import AgeRange


class AgeRangeFilter(filters.FilterSet):
    class Meta:
        model = AgeRange
        fields = ("type",)
