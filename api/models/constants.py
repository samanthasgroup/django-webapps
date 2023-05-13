from enum import IntEnum


class CoordinatorGroupLimit(IntEnum):
    MIN = 5
    MAX = 20


STUDENT_CLASS_MISS_LIMIT = 3
"""If a student misses this amount of classes **in a row** and **without notifying**
the teacher, they can be expelled.
"""

DEFAULT_CHAR_FIELD_MAX_LEN = 255
DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH = 50

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


ENROLLMENT_TEST_PASS_THRESHOLD = 0.7

# FIXME Just an example, subject to change,
#  and also probably levels should be TextChoices
LEVEL_BY_PERCENTAGE_OF_CORRECT_ANSWERS = {
    10: "A1",
    20: "A2",
    40: "B1",
    60: "B2",
}

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
