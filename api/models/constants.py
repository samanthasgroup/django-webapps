DEFAULT_CHAR_FIELD_MAX_LEN = 255
DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH = 15

# IMPORTANT: the boundaries of larger ranges must match the boundaries of the smaller ones

# Match string ranges that are presented to the user to actual ranges, e.g.:
# {"6-8": (6, 9), "9-11": (9, 12), ...}
STUDENT_AGE_RANGE_BOUNDARIES = {
    str_range: (int(str_range.split("-")[0]), int(str_range.split("-")[1]) + 1)
    for str_range in (
        "6-8",
        "9-11",
        "12-14",
        "15-17",
        "18-20",
        "21-25",
        "26-30",
        "31-35",
        "36-40",
        "41-45",
        "46-50",
        "51-55",
        "56-60",
        "61-65",
        "66-70",
        "71-75",
        "76-80",
        "81-65",
        "86-90",
        "91-95",
    )
}

# Match string ranges presented to the teacher (for them to choose desired age groups of students)
# to actual ranges
STUDENT_AGE_RANGE_BOUNDARIES_FOR_TEACHER = {
    "6-11": (6, 12),
    "12-17": (12, 18),
    "18-": (18, 95),
}

# age ranges for matching algorithm
STUDENT_AGE_RANGE_BOUNDARIES_FOR_MATCHING = ()  # TODO
