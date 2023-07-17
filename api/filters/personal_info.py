from django_filters import rest_framework as filters

from api.models import PersonalInfo


class PersonalInfoFilter(filters.FilterSet):
    class Meta:
        model = PersonalInfo
        fields = ("registration_telegram_bot_chat_id",)
