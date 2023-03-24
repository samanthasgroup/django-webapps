from api.views.age_range import AgeRangeViewSet
from api.views.day_and_time_slot import DayAndTimeSlotViewSet
from api.views.language_and_level import LanguageAndLevelViewSet
from api.views.personal_info import PersonalInfoViewSet
from api.views.student import StudentViewSet
from api.views.teacher import TeacherViewSet
from api.views.teacher_under_18 import TeacherUnder18ViewSet

__all__ = [
    "AgeRangeViewSet",
    "DayAndTimeSlotViewSet",
    "LanguageAndLevelViewSet",
    "PersonalInfoViewSet",
    "StudentViewSet",
    "TeacherViewSet",
    "TeacherUnder18ViewSet",
]