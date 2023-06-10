from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AgeRangeViewSet,
    DayAndTimeSlotViewSet,
    EnrollmentTestResultViewSet,
    EnrollmentTestViewSet,
    LanguageAndLevelViewSet,
    NonTeachingHelpViewSet,
    PersonalInfoViewSet,
    PublicGroupViewSet,
    PublicStudentViewSet,
    PublicStudentWithPersonalInfoViewSet,
    PublicTeacherViewSet,
    PublicTeacherWithPersonalInfoViewSet,
    StudentViewSet,
    TeacherUnder18ViewSet,
    TeacherViewSet,
)
from api.views.log_event import (
    CoordinatorLogEventViewSet,
    GroupLogEventViewSet,
    StudentLogEventViewSet,
    TeacherLogEventViewSet,
    TeacherUnder18LogEventViewSet,
)

internal_router = DefaultRouter()
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
internal_router.register(
    r"coordinator_log_events", CoordinatorLogEventViewSet, basename="coordinator_log_events"
)
internal_router.register(r"group_log_events", GroupLogEventViewSet, basename="group_log_events")
internal_router.register(
    r"student_log_events", StudentLogEventViewSet, basename="student_log_events"
)
internal_router.register(
    r"teacher_log_events", TeacherLogEventViewSet, basename="teacher_log_events"
)
internal_router.register(
    r"teacher_under_18_log_events",
    TeacherUnder18LogEventViewSet,
    basename="teacher_under_18_log_events",
)


public_router = DefaultRouter()
public_router.register(r"students", PublicStudentViewSet, basename="students")
public_router.register(
    r"students_with_personal_info",
    PublicStudentWithPersonalInfoViewSet,
    basename="students_with_personal_info",
)
public_router.register(r"groups", PublicGroupViewSet, basename="groups")
public_router.register(r"teachers", PublicTeacherViewSet, basename="teachers")
public_router.register(
    r"teachers_with_personal_info",
    PublicTeacherWithPersonalInfoViewSet,
    basename="teachers_with_personal_info",
)

# "Internal" API is used by bot and "public" API is used by the Tooljet
urlpatterns = [
    path("", include(internal_router.urls)),
    path("public/", include(public_router.urls)),
]
