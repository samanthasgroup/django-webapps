from api.views.age_range import AgeRangeViewSet
from api.views.coordinator import CoordinatorViewSet
from api.views.day_and_time_slot import DayAndTimeSlotViewSet
from api.views.enrollment_test import EnrollmentTestResultViewSet, EnrollmentTestViewSet
from api.views.group import DashboardGroupViewSet, GroupViewSet
from api.views.language_and_level import LanguageAndLevelViewSet
from api.views.non_teaching_help import NonTeachingHelpViewSet
from api.views.personal_info import PersonalInfoViewSet
from api.views.student import DashboardStudentViewSet, DashboardStudentWithPersonalInfoViewSet, StudentViewSet
from api.views.teacher import DashboardTeacherViewSet, DashboardTeacherWithPersonalInfoViewSet, TeacherViewSet
from api.views.teacher_under_18 import TeacherUnder18ViewSet

__all__ = [
    "AgeRangeViewSet",
    "DayAndTimeSlotViewSet",
    "LanguageAndLevelViewSet",
    "NonTeachingHelpViewSet",
    "PersonalInfoViewSet",
    "StudentViewSet",
    "GroupViewSet",
    "DashboardGroupViewSet",
    "DashboardStudentViewSet",
    "DashboardStudentWithPersonalInfoViewSet",
    "DashboardTeacherViewSet",
    "DashboardTeacherWithPersonalInfoViewSet",
    "TeacherViewSet",
    "TeacherUnder18ViewSet",
    "EnrollmentTestViewSet",
    "EnrollmentTestResultViewSet",
    "CoordinatorViewSet",
]
