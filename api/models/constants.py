DEFAULT_CHAR_FIELD_MAX_LEN = 255
DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH = 15

# IMPORTANT: the boundaries of larger ranges must match the boundaries of the smaller ones

# Match string ranges that are presented to the user to actual ranges.
# A dict comprehension would be more concise but less readable.  Dict comprehension would also be
# less error-prone, but the dict isn't supposed to be changed frequently (or at all) after launch.
STUDENT_AGE_RANGES = {
    "5-6": (5, 7),
    "7-8": (7, 9),
    "9-10": (9, 11),
    "11-12": (11, 13),
    "13-14": (13, 15),
    "15-17": (15, 18),
    "18-20": (18, 21),
    "21-25": (21, 26),
    "26-30": (26, 31),
    "31-35": (31, 36),
    "36-40": (36, 41),
    "41-45": (41, 46),
    "46-50": (46, 51),
    "51-55": (51, 56),
    "56-60": (56, 61),
    "61-65": (61, 66),
    "66-70": (66, 71),
    "71-75": (71, 76),
    "76-80": (76, 81),
    "81-65": (81, 66),
    "86-90": (86, 91),
    "91-95": (91, 96),
}

# Match string ranges presented to the teacher (for them to choose desired age groups of students)
# to actual ranges
STUDENT_AGE_RANGES_FOR_TEACHER = {
    "6-11": (6, 12),
    "12-17": (12, 18),
    "18-": (18, 95),
}

# age ranges for matching algorithm
STUDENT_AGE_RANGES_FOR_MATCHING = ()  # TODO
