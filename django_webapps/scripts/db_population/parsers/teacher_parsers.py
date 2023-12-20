import re

from email_validator import validate_email

from api.models.choices.status.project import TeacherProjectStatus
from api.models.choices.status.situational import TeacherSituationalStatus


def parse_project_status(status_str: str) -> TeacherProjectStatus | None:
    status_str = status_str.lower()
    if status_str in ["идут занятия"]:
        return TeacherProjectStatus.WORKING
    if status_str in ["перерыв в преподавании"]:
        return TeacherProjectStatus.FINISHED_STAYS
    if status_str in ["закончил участие в проекте"]:
        return TeacherProjectStatus.FINISHED_LEFT
    if status_str in ["готов начать позже (см.коммент)"]:
        pass
    if status_str in ["Substitute Teacher"]:
        pass
    if status_str in ["Speaking Clubs"]:
        pass
    if status_str in ["жду ответа"]:
        pass
    if status_str in ["не сможет участвовать в проекте"]:
        pass
    if status_str in ["ищу учеников"]:
        pass
    if status_str in ["CV and Interview"]:
        pass
    if status_str in ["дубль"]:  # duplicate?
        pass
    return None


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
    except Exception as _:
        return None
    return email_str


def parse_has_expirience(exp_str: str) -> bool:
    if exp_str.lower() == "да":
        return True
    return False


def parse_telegram_name(tg_str: str) -> str | None:
    tg_regex = re.compile(r"@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*")
    match_result = re.findall(tg_regex, tg_str)
    if len(match_result) > 0:
        return match_result[0]
    return None


def parse_can_give_feedback(fd_str: str) -> bool:
    if fd_str.lower() == "да":
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
    if age_ranges_str.lower() == "да":
        return True
    return False


def parse_language_level(level_str: str) -> list[str]:
    if "any" in level_str.lower() or "любой" in level_str.lower():
        return ["A0", "A1", "A2", "B1", "B2"]
    regex = re.compile(r"A0|A1|A2|B1|B2")
    result = re.findall(regex, level_str.upper())
    return list(set(result))


def parse_availability_slots(
    slot_str: str, time_slots: list[tuple[int, int]] | None = None
) -> list[tuple[int, int]]:
    if time_slots is None:
        time_slots = [(5, 8), (8, 11), (11, 17), (17, 21)]

    slot_str = slot_str.lower()
    result = []
    if "утро" in slot_str or "morning" in slot_str:
        result.extend([(8, 11), (5, 8)])
    if "вечер" in slot_str or "evening" in slot_str:
        result.append((17, 21))
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
    if club_str.lower() == "да":
        return True
    return False
