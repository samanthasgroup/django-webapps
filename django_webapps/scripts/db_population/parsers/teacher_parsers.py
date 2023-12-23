import re
from enum import Enum

from email_validator import EmailNotValidError, validate_email

from api.models.auxil.constants import TIME_SLOTS, LanguageLevelId
from api.models.choices.status.project import TeacherProjectStatus
from api.models.choices.status.situational import TeacherSituationalStatus


class ProjectStatusAction(str, Enum):
    SPEAKING_CLUB = "speking_club"
    CV_AND_INTERVIEW = "cv_and_interview"
    NONE = "none"


def parse_project_status(
    status_str: str,
) -> tuple[TeacherProjectStatus, ProjectStatusAction] | None:
    status_str = status_str.lower()
    result = None
    if status_str in ["идут занятия"]:
        result = (TeacherProjectStatus.WORKING, ProjectStatusAction.NONE)
    elif status_str in ["перерыв в преподавании"]:
        result = (TeacherProjectStatus.ON_LEAVE, ProjectStatusAction.NONE)
    elif status_str in ["закончил участие в проекте"]:
        result = (TeacherProjectStatus.FINISHED_LEFT, ProjectStatusAction.NONE)
    elif status_str in ["готов начать позже (см.коммент)"]:  # noqa: SIM114
        pass
    elif status_str in ["Substitute Teacher"]:
        pass
    elif status_str in ["Speaking Clubs"]:
        result = (TeacherProjectStatus.WORKING, ProjectStatusAction.SPEAKING_CLUB)
    elif status_str in ["жду ответа", "ищу учеников"]:
        result = (TeacherProjectStatus.NO_GROUP_YET, ProjectStatusAction.NONE)
    elif status_str in ["не сможет участвовать в проекте"]:
        pass
    elif status_str in ["CV and Interview"]:
        result = (TeacherProjectStatus.NO_GROUP_YET, ProjectStatusAction.CV_AND_INTERVIEW)
    elif status_str in ["дубль"]:  # duplicate?
        pass
    return result


def parse_situational_status(status_str: str) -> TeacherSituationalStatus | None:
    status_str = status_str.lower()
    if status_str in ["не вышел на связь"]:
        return TeacherSituationalStatus.NO_RESPONSE
    if status_str in ["группы набраны"]:
        return TeacherSituationalStatus.AWAITING_START
    return None


def parse_name(name_str: str) -> str:
    return name_str


def parse_email(email_str: str) -> str | None:
    try:
        validate_email(email_str)
    except EmailNotValidError as _:
        return None
    return email_str


def parse_has_experience(exp_str: str) -> bool:
    if exp_str.lower().strip() == "да":
        return True
    return False


def parse_telegram_name(tg_str: str) -> str | None:
    tg_regex = re.compile(r"@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*")
    match_result = re.search(tg_regex, tg_str)
    if match_result is not None:
        return match_result.group(0)
    return None


def parse_can_give_feedback(fd_str: str) -> bool:
    if fd_str.lower().strip() == "да":
        return True
    return False


def parse_weekly_frequency(freq_str: str) -> int | None:
    if "мин" in freq_str.lower() or "час" in freq_str.lower():
        return 1
    numbers = list(map(int, re.findall(r"\d+", str(freq_str))))
    if len(numbers) > 0:
        return max(numbers)
    return None


def parse_age_ranges(age_ranges_str: str) -> bool:
    if age_ranges_str.lower().strip() == "да":
        return True
    return False


def parse_language_level(level_str: str) -> list[str]:
    language_levels = [e.value for e in LanguageLevelId]
    if "any" in level_str.lower() or "любой" in level_str.lower():
        return language_levels
    regex = re.compile(rf"{'|'.join(language_levels)}")
    result = re.findall(regex, level_str.upper())
    return list(set(result))


def parse_availability_slots(
    slot_str: str, time_slots: list[tuple[int, int]] | None = None
) -> list[tuple[int, int]]:
    if time_slots is None:
        time_slots = TIME_SLOTS

    slot_str = slot_str.lower()
    result = []
    if "утро" in slot_str or "morning" in slot_str:
        result.extend([(8, 11), (5, 8)])
    if "вечер" in slot_str or "evening" in slot_str:
        result.extend(
            [
                (11, 14),
                (14, 17),
            ]
        )
    if "день" in slot_str or "afternoon" in slot_str:
        result.append((11, 17))
    if len(result) > 0:
        return result

    regex = re.compile(r"(\d{1,2}):(\d{1,2})-(\d{1,2}):(\d{1,2})")
    slot_str = slot_str.replace(" ", "").replace(".", ":")

    def find_best_fits(range_to_fit: tuple[int, int]) -> list[tuple[int, int]]:
        result = []
        for slot in time_slots:
            if slot[0] >= range_to_fit[0] and slot[1] <= range_to_fit[1]:
                result.append(slot)
        return result

    re_results = re.findall(regex, slot_str)
    if len(re_results) > 0:
        for re_result in re_results:
            range_to_fit = (int(re_result[0]), int(re_result[2]))
            result.extend(find_best_fits(range_to_fit))
    return list(set(result))


def parse_non_teaching_help(help_str: str) -> bool:
    if len(help_str) > 1:
        return True
    return False


def parse_speaking_club(club_str: str) -> bool:
    if club_str.lower().strip() == "да":
        return True
    return False
