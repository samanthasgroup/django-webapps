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
        (81, 65),
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
        (18, 95),
    )
}

# age ranges for matching algorithm
# TODO for now leaving these ranges the same as the ranges that students get when registering,
#  but this is likely to change.  The children's ranges will most likely remain the same, though.
STUDENT_AGE_RANGES_FOR_MATCHING = STUDENT_AGE_RANGES.copy()
