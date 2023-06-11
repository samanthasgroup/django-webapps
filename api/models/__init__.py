from .age_ranges import AgeRange
from .base import GroupOrPerson
from .days_time_slots import DayAndTimeSlot, TimeSlot
from .enrollment_tests import (
    EnrollmentTest,
    EnrollmentTestQuestion,
    EnrollmentTestQuestionOption,
    EnrollmentTestResult,
)
from .groups import Group, SpeakingClub
from .languages_levels import Language, LanguageAndLevel, LanguageLevel
from .log_events import (
    CoordinatorLogEvent,
    GroupLogEvent,
    LogEvent,
    StudentLogEvent,
    TeacherLogEvent,
    TeacherUnder18LogEvent,
)
from .non_teaching_help import NonTeachingHelp
from .people import Coordinator, PersonalInfo, Student, Teacher, TeacherUnder18

# for mypy: listing only models that appear in admin.py
__all__ = [
    "Coordinator",
    "CoordinatorLogEvent",
    "EnrollmentTest",
    "EnrollmentTestQuestion",
    "EnrollmentTestQuestionOption",
    "Group",
    "GroupLogEvent",
    "SpeakingClub",
    "PersonalInfo",
    "Student",
    "StudentLogEvent",
    "Teacher",
    "TeacherLogEvent",
    "TeacherUnder18",
    "TeacherUnder18LogEvent",
    "Language",
    "LanguageAndLevel",
    "AgeRange",
    "TimeSlot",
    "DayAndTimeSlot",
    "EnrollmentTestResult",
    "NonTeachingHelp",
]
