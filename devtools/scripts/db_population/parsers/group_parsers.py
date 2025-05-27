from api.models.choices.status.project import GroupProjectStatus

RAW_PROJECT_STATUS_TO_PARSED: dict[str, GroupProjectStatus] = {
    "группа расформирована": GroupProjectStatus.FINISHED,
    "уровень завершен": GroupProjectStatus.FINISHED,
    "идет набор": GroupProjectStatus.WORKING,
    "нет набор": GroupProjectStatus.AWAITING_START,
}


LANGUAGES_MAPPING: dict[str, str] = {
    "русский": "Russian",
    "украинский": "Ukrainian",
    "немецкий": "German",
    "испанский": "Spanish",
    "итальянский": "Italian",
    "английский": "English",
    "французский": "French",
    "шведский": "Swedish",
    "финский": "Finnish",
    "польский": "Polish",
    "португальский": "Portuguese",
    "венгерский": "Hungarian",
    "чешский": "Czech",
    "греческий": "Greek",
    "японский": "Japanese",
}


def parse_status(
    status_str: str,
) -> GroupProjectStatus | None:
    status_str = status_str.strip().rstrip().lower()
    return RAW_PROJECT_STATUS_TO_PARSED.get(status_str)


def parse_languages(input_str: str) -> list[str]:
    input_str = input_str.strip().rstrip().replace("/", ",")
    results: list[str] = []
    for lan in input_str.split(","):
        result = LANGUAGES_MAPPING.get(lan.strip().rstrip().lower())
        if result:
            results.append(result)
    return results
