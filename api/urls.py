from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AgeRangeViewSet,
    DayAndTimeSlotViewSet,
    LanguageAndLevelViewSet,
    NonTeachingHelpViewSet,
    PersonalInfoViewSet,
    StudentViewSet,
    TeacherUnder18ViewSet,
    TeacherViewSet,
)

router = DefaultRouter()
router.register(r"personal_info", PersonalInfoViewSet, basename="personal_info")
router.register(r"students", StudentViewSet, basename="students")
router.register(r"teachers", TeacherViewSet, basename="teachers")
router.register(r"teachers_under_18", TeacherUnder18ViewSet, basename="teachers_under_18")
router.register(r"age_ranges", AgeRangeViewSet, basename="age_ranges")
router.register(r"languages_and_levels", LanguageAndLevelViewSet, basename="languages_and_levels")
router.register(r"day_and_time_slots", DayAndTimeSlotViewSet, basename="day_and_time_slots")
router.register(r"non_teaching_help", NonTeachingHelpViewSet, basename="non_teaching_help")

urlpatterns = [
    path("", include(router.urls)),
]
