import re
from enum import Enum

from api.models.choices.status.project import TeacherProjectStatus
from api.models.choices.status.situational import TeacherSituationalStatus


class ProjectStatusAction(str, Enum):
    SPEAKING_CLUB = "speking_club"
    CV_AND_INTERVIEW = "cv_and_interview"
    NONE = "none"


RAW_PROJECT_STATUS_TO_PARSED: dict[
    str, tuple[TeacherSituationalStatus | None, TeacherProjectStatus, ProjectStatusAction]
] = {
    "идут занятия": (None, TeacherProjectStatus.WORKING, ProjectStatusAction.NONE),
    "перерыв в преподавании": (None, TeacherProjectStatus.ON_LEAVE, ProjectStatusAction.NONE),
    "закончил участие в проекте": (
        None,
        TeacherProjectStatus.FINISHED_LEFT,
        ProjectStatusAction.NONE,
    ),
    "speaking clubs": (None, TeacherProjectStatus.WORKING, ProjectStatusAction.SPEAKING_CLUB),
    "жду ответа": (None, TeacherProjectStatus.NO_GROUP_YET, ProjectStatusAction.NONE),
    "ищу учеников": (None, TeacherProjectStatus.NO_GROUP_YET, ProjectStatusAction.NONE),
    "cv and interview": (
        None,
        TeacherProjectStatus.NO_GROUP_YET,
        ProjectStatusAction.CV_AND_INTERVIEW,
    ),
    "готов начать позже (см.коммент)": (
        None,
        TeacherProjectStatus.NO_GROUP_YET,
        ProjectStatusAction.NONE,
    ),
    "substitute teacher": (None, TeacherProjectStatus.WORKING, ProjectStatusAction.NONE),
    "группы набраны": (
        TeacherSituationalStatus.AWAITING_START,
        TeacherProjectStatus.WORKING,
        ProjectStatusAction.NONE,
    ),
    "не вышел на связь": (
        TeacherSituationalStatus.NO_RESPONSE,
        TeacherProjectStatus.NO_GROUP_YET,
        ProjectStatusAction.NONE,
    ),
}


def parse_status(
    status_str: str,
) -> tuple[TeacherSituationalStatus | None, TeacherProjectStatus, ProjectStatusAction] | None:
    status_str = status_str.lower().strip()
    return RAW_PROJECT_STATUS_TO_PARSED.get(status_str)


def parse_can_give_feedback(fd_str: str) -> bool:
    return fd_str.lower().strip() == "да"


def parse_groups_number(groups_str: str) -> int | None:
    if "мин" in groups_str.lower() or "час" in groups_str.lower():
        return 1
    numbers = list(map(int, re.findall(r"\d+", groups_str)))
    if len(numbers) > 0:
        return max(numbers)
    return None


def parse_age_ranges(age_ranges_str: str) -> bool:
    return age_ranges_str.lower().strip() == "да"


def parse_speaking_club(club_str: str) -> bool:
    return club_str.lower().strip() == "да"


def parse_has_experience(experience: str) -> bool:
    return experience.lower().strip() == "да"
