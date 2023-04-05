from django_filters import rest_framework as filters

from api.models import EnrollmentTest


class EnrollmentTestFilter(filters.FilterSet):
    class Meta:
        model = EnrollmentTest
        fields = (
            "age_ranges",
            "levels",
            "language",
        )
