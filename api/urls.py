from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AgeRangeViewSet,
    DashboardGroupViewSet,
    DashboardStudentViewSet,
    DashboardStudentWithPersonalInfoViewSet,
    DashboardTeacherViewSet,
    DashboardTeacherWithPersonalInfoViewSet,
    DayAndTimeSlotViewSet,
    EnrollmentTestResultViewSet,
    EnrollmentTestViewSet,
    GroupViewSet,
    LanguageAndLevelViewSet,
    NonTeachingHelpViewSet,
    PersonalInfoViewSet,
    StudentViewSet,
    TeacherUnder18ViewSet,
    TeacherViewSet,
)
from api.views.personal_info import DashboardPersonalInfoViewSet

internal_router = DefaultRouter()
internal_router.register(r"groups", GroupViewSet, basename="groups")
internal_router.register(r"personal_info", PersonalInfoViewSet, basename="personal_info")
internal_router.register(r"students", StudentViewSet, basename="students")
internal_router.register(r"teachers", TeacherViewSet, basename="teachers")
internal_router.register(r"teachers_under_18", TeacherUnder18ViewSet, basename="teachers_under_18")
internal_router.register(r"age_ranges", AgeRangeViewSet, basename="age_ranges")
internal_router.register(
    r"languages_and_levels", LanguageAndLevelViewSet, basename="languages_and_levels"
)
internal_router.register(
    r"day_and_time_slots", DayAndTimeSlotViewSet, basename="day_and_time_slots"
)
internal_router.register(r"enrollment_test", EnrollmentTestViewSet, basename="enrollment_test")
internal_router.register(
    r"enrollment_test_result", EnrollmentTestResultViewSet, basename="enrollment_test_result"
)
internal_router.register(
    r"non_teaching_help", NonTeachingHelpViewSet, basename="non_teaching_help"
)

dashboard_router = DefaultRouter()
dashboard_router.register(r"students", DashboardStudentViewSet, basename="students")
dashboard_router.register(
    r"students_with_personal_info",
    DashboardStudentWithPersonalInfoViewSet,
    basename="students_with_personal_info",
)
dashboard_router.register(r"groups", DashboardGroupViewSet, basename="groups")
dashboard_router.register(r"teachers", DashboardTeacherViewSet, basename="teachers")
dashboard_router.register(
    r"teachers_with_personal_info",
    DashboardTeacherWithPersonalInfoViewSet,
    basename="teachers_with_personal_info",
)
dashboard_router.register(
    "personal_info",
    DashboardPersonalInfoViewSet,
    basename="personal_info",
)
dashboard_router.register(
    r"languages_and_levels", LanguageAndLevelViewSet, basename="languages_and_levels"
)
dashboard_router.register(
    r"day_and_time_slots", DayAndTimeSlotViewSet, basename="day_and_time_slots"
)

# "Internal" API is used by bot and "dashboard" API is used by the Tooljet
urlpatterns = [
    path("", include(internal_router.urls)),
    path("dashboard/", include(dashboard_router.urls)),
]
