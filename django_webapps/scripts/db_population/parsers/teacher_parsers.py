import re
from enum import Enum

from api.models.auxil.constants import TIME_SLOTS, LanguageLevelId
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
        TeacherProjectStatus.ON_LEAVE,
        ProjectStatusAction.NONE,
    ),
}


def parse_status(
    status_str: str,
) -> tuple[TeacherSituationalStatus | None, TeacherProjectStatus, ProjectStatusAction] | None:
    status_str = status_str.lower().strip()
    return RAW_PROJECT_STATUS_TO_PARSED.get(status_str)


def parse_name(name_str: str) -> str:
    return name_str


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


def parse_language_level(level_str: str) -> list[str]:
    language_levels = [e.value for e in LanguageLevelId]
    if "any" in level_str.lower() or "любой" in level_str.lower():
        return language_levels
    level_str = level_str.upper().replace("А", "A").replace("В", "B").replace("С", "C")
    regex = re.compile(rf"{'|'.join(language_levels)}")
    result = re.findall(regex, level_str.upper())
    return list(set(result))


def parse_availability_slots(
    slot_str: str,
    time_slots: tuple[
        tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
    ] = TIME_SLOTS,
) -> list[tuple[int, int]]:
    slot_str = slot_str.lower().strip()
    result = []

    def find_best_fits(range_to_fit: tuple[int, int]) -> list[tuple[int, int]]:
        result = []
        for slot in time_slots:
            if slot[0] >= range_to_fit[0] and slot[1] <= range_to_fit[1]:
                result.append(slot)
        return result

    # parse till|from some time, e.g. till 14:00, from 05:00
    regex_till = re.compile(r"(till|до|c|from|после)(\d{1,2})")
    re_result = re.search(regex_till, slot_str)
    if re_result:
        re_groups = re_result.groups()
        if re_groups[0] in ["с", "после", "from"]:
            range_to_fit = (int(re_groups[1]), 21)
        else:
            range_to_fit = (5, int(re_groups[1]))
        result.extend(find_best_fits(range_to_fit))
    if len(result) > 0:
        return result

    # parse slots
    # e.g. 11:00-17:00, 11-17, 11.17 and so on
    regex_slots = re.compile(
        r"(\d{1,2})[.\-:]{0,1}(\d{1,2}){0,1}[\-.](\d{1,2})[.\-:]{0,1}(\d{1,2}){0,1}"
    )
    slot_str = slot_str.replace(" ", "")

    re_results = re.findall(regex_slots, slot_str)
    if len(re_results) > 0:
        for re_groups in re_results:
            # skip minutes for now, only hours
            range_to_fit = (int(re_groups[0]), int(re_groups[2]))
            result.extend(find_best_fits(range_to_fit))
    if len(result) > 0:
        return list(set(result))

    # parse parts of day
    if "утро" in slot_str or "morning" in slot_str:
        result.extend([(8, 11), (5, 8)])
    if "вечер" in slot_str or "evening" in slot_str:
        result.append((17, 21))
    if "день" in slot_str or "afternoon" in slot_str:
        result.extend([(11, 14), (14, 17)])

    return result


def parse_speaking_club(club_str: str) -> bool:
    return club_str.lower().strip() == "да"


def parse_has_experience(experience: str) -> bool:
    return experience.lower().strip() == "да"
