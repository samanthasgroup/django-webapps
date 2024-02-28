import re

from api.models.auxil.constants import STUDENT_AGE_RANGES
from api.models.choices.status.project import StudentProjectStatus
from api.models.choices.status.situational import StudentSituationalStatus

RAW_PROJECT_STATUS_TO_PARSED: dict[
    str, tuple[StudentSituationalStatus | None, StudentProjectStatus]
] = {
    "группа расформирована": (None, StudentProjectStatus.FINISHED),
    "не ходит на занятия": (StudentSituationalStatus.NOT_ATTENDING, StudentProjectStatus.STUDYING),
    "идут занятия": (None, StudentProjectStatus.STUDYING),
    "нет ответа": (StudentSituationalStatus.NO_RESPONSE, StudentProjectStatus.NO_GROUP_YET),
    "перестал отвечать": (StudentSituationalStatus.NO_RESPONSE, StudentProjectStatus.NO_GROUP_YET),
    "вышел на связь, ожидает старта занятий": (
        StudentSituationalStatus.AWAITING_START,
        StudentProjectStatus.STUDYING,
    ),
    "уточнение расписания": (None, StudentProjectStatus.NO_GROUP_YET),
    "жду ответа": (StudentSituationalStatus.NO_RESPONSE, StudentProjectStatus.NO_GROUP_YET),
    "БЛОК УЧЕНИКА (коммент)": (None, StudentProjectStatus.BANNED),
    "заблокирована": (None, StudentProjectStatus.BANNED),
    "2 - нет ответа": (StudentSituationalStatus.NO_RESPONSE, StudentProjectStatus.NO_GROUP_YET),
    "уровень завершен": (None, StudentProjectStatus.FINISHED),
}


def parse_status(
    status_str: str,
) -> tuple[StudentSituationalStatus | None, StudentProjectStatus] | None:
    status_str = status_str.strip().rstrip()
    return RAW_PROJECT_STATUS_TO_PARSED.get(status_str)


def parse_age_range(age_range_str: str) -> tuple[int, int] | None:
    age_range_str = age_range_str.strip().rstrip().replace(" ", "")
    regex = r"(\d+)-?(\d+)?"
    search_result = re.search(regex, age_range_str)
    if search_result is None:
        raise ValueError(f"Unable to parse age range {age_range_str}")

    from_age, to_age = search_result.groups()
    if to_age is None:
        to_age = from_age
    to_age = int(to_age)
    from_age = int(from_age)
    for from_age_defined, to_age_defined in STUDENT_AGE_RANGES.values():
        if from_age_defined <= from_age:
            return (from_age_defined, to_age_defined)
    raise ValueError(f"Unable to parse age range {age_range_str}")
