from rest_framework import serializers

from api.models import people
from api.serializers.statuses import StudentStatusSerializer


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = people.PersonalInfo
        fields = [
            "id",
            "date_and_time_added",
            "first_name",
            "last_name",
            "tg_username",
            "email",
            "phone",
            "utc_timedelta",
            "information_source",
            "communication_language_mode",
            "availability_slots",
            "registration_bot_chat_id",
            "chatwoot_conversation_id",
            "comment",
        ]


class StudentSerializer(serializers.ModelSerializer):
    personal_info = PersonalInfoSerializer()
    status = StudentStatusSerializer()

    class Meta:
        model = people.Student
        fields = [
            "personal_info",
            "age_range",
            "is_member_of_speaking_club",
            "requires_help_with_CV",
            "status",
        ]


"""       
class TeacherInfoSerializer(serializers.ModelSerializer):
    personal_info = PersonalInfoSerializer()
    teacher_status = TeacherStatusSerializer()
    
    class Meta:
        model = people.Student
        fields = ['personal_info', 'age_range', 'is_member_of_speaking_club',
                  'requires_help_with_CV', 'student_status']
    
        categories = models.ManyToManyField(TeacherCategory)
    has_prior_teaching_experience = models.BooleanField()
    simultaneous_groups = models.IntegerField(
        default=1, help_text="Number of groups the teacher can teach simultaneously"
    )
    status = models.ForeignKey(TeacherStatus, on_delete=models.PROTECT)
    student_age_ranges = models.ManyToManyField(
        AgeRange,
        help_text="Age ranges of students that the teacher is willing to teach. "
        "The 'from's and 'to's of these ranges are wider than those the students choose "
        "for themselves.",
    )
    teaching_languages_and_levels = models.ManyToManyField(TeachingLanguageAndLevel)
    weekly_frequency_per_group = models.IntegerField(
        help_text="Number of times per week the teacher can have classes with each group"
"""
