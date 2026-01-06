from api.models.shared_abstract.group_or_person import GroupOrPerson

from .age_range import AgeRange
from .coordinator import Coordinator
from .day_and_time_slot import DayAndTimeSlot, TimeSlot
from .enrollment_test import EnrollmentTest, EnrollmentTestQuestion, EnrollmentTestQuestionOption, EnrollmentTestResult
from .group import Group, SpeakingClub
from .language_and_level import Language, LanguageAndLevel, LanguageLevel
from .log_event import (
    CoordinatorLogEvent,
    GroupLogEvent,
    LogEvent,
    StudentLogEvent,
    TeacherLogEvent,
    TeacherUnder18LogEvent,
)
from .non_teaching_help import NonTeachingHelp
from .personal_info import PersonalInfo
from .role import Role
from .student import Student
from .teacher import Teacher
from .teacher_under_18 import TeacherUnder18

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
    "Role",
]
