from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AgeRangeViewSet,
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

urlpatterns = [
    path("", include(router.urls)),
]
