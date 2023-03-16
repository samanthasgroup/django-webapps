from .age_ranges import AgeRange
from .base import GroupOrPerson
from .days_time_slots import DayAndTimeSlot, TimeSlot
from .enrollment_tests import (
    EnrollmentTest,
    EnrollmentTestQuestion,
    EnrollmentTestQuestionOption,
    EnrollmentTestResult,
)
from .groups import Group
from .languages_levels import Language, LanguageAndLevel, LanguageLevel
from .log_events import (
    CoordinatorLogEvent,
    GroupLogEvent,
    LogEvent,
    PersonLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
)
from .people import Coordinator, PersonalInfo, Student, Teacher, TeacherUnder18

# for mypy: listing only models that appear in admin.my
__all__ = [
    "Coordinator",
    "EnrollmentTest",
    "EnrollmentTestQuestion",
    "EnrollmentTestQuestionOption",
    "Group",
    "PersonalInfo",
    "Student",
    "Teacher",
    "TeacherUnder18",
    "Language",
    "LanguageAndLevel",
]
