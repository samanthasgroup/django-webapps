from django_filters import rest_framework as filters

from api.models import LanguageAndLevel


class LanguageAndLevelFilter(filters.FilterSet):
    class Meta:
        model = LanguageAndLevel
        fields = ("language",)
