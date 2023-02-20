from rest_framework import serializers
from api.models import people


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = people.PersonalInfo
        fields = ['id', 'date_and_time_added', 'first_name', 'last_name', 'tg_username',
                  'email', 'phone', 'tz_summer_relative_to_utc', 'tz_winter_relative_to_utc',
                  'age', 'information_source', 'native_languages', 'availability_slots',
                  'registration_bot_chat_id', 'chatwoot_conversation_id', 'comment']