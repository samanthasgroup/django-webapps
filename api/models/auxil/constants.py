from enum import Enum, IntEnum


class CoordinatorGroupLimit(IntEnum):
    MIN = 5
    MAX = 20


class LanguageLevelId(str, Enum):
    A0_BEGINNER = "A0"
    A1_ELEMENTARY = "A1"
    A2_PRE_INTERMEDIATE = "A2"
    B1_INTERMEDIATE = "B1"
    B2_UPPER_INTERMEDIATE = "B2"
    C1_PRE_ADVANCED = "C1"
    # No C2 at this school


DEFAULT_CHAR_FIELD_MAX_LEN = 255
DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH = 50

ENROLLMENT_TEST_LEVEL_THRESHOLDS_FOR_NUMBER_OF_QUESTIONS = {
    25: {
        5: LanguageLevelId.A1_ELEMENTARY,
        11: LanguageLevelId.A2_PRE_INTERMEDIATE,
        19: LanguageLevelId.B1_INTERMEDIATE,
    },
    35: {
        6: LanguageLevelId.A1_ELEMENTARY,
        13: LanguageLevelId.A2_PRE_INTERMEDIATE,
        20: LanguageLevelId.B1_INTERMEDIATE,
        27: LanguageLevelId.B2_UPPER_INTERMEDIATE,
        32: LanguageLevelId.C1_PRE_ADVANCED,
    },
}

# IMPORTANT: the boundaries of larger ranges must match the boundaries of the smaller ones

# Match string ranges that are presented to the user to actual ranges: {"5-6": (5, 6), ...}
STUDENT_AGE_RANGES = {
    f"{left}-{right}": (left, right)
    for left, right in (
        (5, 6),
        (7, 8),
        (9, 10),
        (11, 12),
        (13, 14),
        (15, 17),
        (18, 20),
        (21, 25),
        (26, 30),
        (31, 35),
        (36, 40),
        (41, 45),
        (46, 50),
        (51, 55),
        (56, 60),
        (61, 65),
        (66, 70),
        (71, 75),
        (76, 80),
        (81, 85),
        (86, 90),
        (91, 95),
    )
}

# Match string ranges presented to the teacher (for them to choose desired age groups of students)
# to actual ranges
STUDENT_AGE_RANGES_FOR_TEACHER = {
    f"{left}-{right}": (left, right)
    for left, right in (
        (5, 8),
        (9, 12),
        (13, 17),
        (18, 65),
        (66, 95),
    )
}

# age ranges for matching algorithm
STUDENT_AGE_RANGES_FOR_MATCHING = {
    f"{left}-{right}": (left, right)
    for left, right in (
        (5, 6),
        (7, 8),
        (9, 10),
        (11, 12),
        (13, 14),
        (15, 17),
        (18, 25),
        (26, 35),
        (36, 45),
        (46, 55),
        (56, 65),
        (66, 75),
        (76, 85),
        (86, 95),
    )
}

STUDENT_CLASS_MISS_LIMIT = 3
"""If a student misses this amount of classes **in a row** and **without notifying**
the teacher, they can be expelled.
"""

TEACHER_PEER_SUPPORT_FIELD_NAME_PREFIX = "peer_support_"

TEACHER_PEER_SUPPORT_OPTIONS = [
    "can_check_syllabus",
    "can_host_mentoring_sessions",
    "can_give_feedback",
    "can_help_with_childrens_groups",
    "can_provide_materials",
    "can_invite_to_class",
    "can_work_in_tandem",
]
