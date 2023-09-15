from api.serializers.age_range import AgeRangeSerializer
from api.serializers.day_and_time_slot import DayAndTimeSlotSerializer
from api.serializers.enrollment_test import (
    EnrollmentTestResultCreateSerializer,
    EnrollmentTestSerializer,
)
from api.serializers.language_and_level import LanguageAndLevelSerializer
from api.serializers.non_teaching_help import NonTeachingHelpSerializer
from api.serializers.personal_info import (
    CheckChatIdExistenceSerializer,
    CheckNameAndEmailExistenceSerializer,
    DashboardPersonalInfoSerializer,
    PersonalInfoSerializer,
)
from api.serializers.student.dashboard import (
    DashboardStudentSerializer,
    DashboardStudentTransferSerializer,
    DashboardStudentWithPersonalInfoSerializer,
)
from api.serializers.student.internal import StudentReadSerializer, StudentWriteSerializer
from api.serializers.student.minified import MinifiedStudentSerializer
from api.serializers.teacher.dashboard import (
    DashboardTeacherSerializer,
    DashboardTeacherTransferSerializer,
    DashboardTeacherWithPersonalInfoSerializer,
)
from api.serializers.teacher.internal import TeacherReadSerializer, TeacherWriteSerializer
from api.serializers.teacher.minified import MinifiedTeacherSerializer
from api.serializers.teacher_under_18 import (
    TeacherUnder18ReadSerializer,
    TeacherUnder18WriteSerializer,
)

# Must be imported at the end because of circular dependency
from api.serializers.group.dashboard import (  # isort:skip
    DashboardGroupSerializer,
    DashboardGroupWithStudentsSerializer,
)

from api.serializers.group.internal import (  # isort:skip
    GroupDiscardSerializer,
    GroupReadSerializer,
    GroupWriteSerializer,
)

__all__ = [
    "AgeRangeSerializer",
    "DayAndTimeSlotSerializer",
    "LanguageAndLevelSerializer",
    "NonTeachingHelpSerializer",
    "CheckChatIdExistenceSerializer",
    "CheckNameAndEmailExistenceSerializer",
    "PersonalInfoSerializer",
    "DashboardPersonalInfoSerializer",
    "DashboardGroupSerializer",
    "GroupReadSerializer",
    "GroupWriteSerializer",
    "DashboardGroupWithStudentsSerializer",
    "DashboardStudentSerializer",
    "DashboardStudentWithPersonalInfoSerializer",
    "DashboardStudentTransferSerializer",
    "DashboardTeacherSerializer",
    "DashboardTeacherWithPersonalInfoSerializer",
    "DashboardTeacherTransferSerializer",
    "StudentReadSerializer",
    "StudentWriteSerializer",
    "MinifiedStudentSerializer",
    "TeacherReadSerializer",
    "TeacherWriteSerializer",
    "MinifiedTeacherSerializer",
    "TeacherUnder18ReadSerializer",
    "TeacherUnder18WriteSerializer",
    "EnrollmentTestSerializer",
    "EnrollmentTestResultCreateSerializer",
    "GroupDiscardSerializer",
]
