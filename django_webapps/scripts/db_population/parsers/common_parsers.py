import datetime
import re

import phonenumbers
import pytz
from email_validator import EmailNotValidError, validate_email
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from api.models.auxil.constants import TIME_SLOTS, LanguageLevelId

MIN_NAME_LENGTH = 2


def _city_to_timezone(city_name: str) -> str | None:
    geolocator = Nominatim(user_agent="city-to-timezone")
    coords = geolocator.geocode(city_name)
    tf = TimezoneFinder()
    if coords:
        return tf.timezone_at(lng=coords.longitude, lat=coords.latitude)

    return None


def parse_timezone(tz_str: str) -> datetime.tzinfo | None:
    tz_name = None
    offset = None
    regex_right = re.compile(r"((UTC|GMT)([\+|\-]\d*))")
    regex_left = re.compile(r"(([\+|\-]\d*)(UTC|GMT))")
    tz_str = tz_str.replace(" ", "").upper()

    match_result_right = re.search(regex_right, tz_str)
    match_result_left = re.search(regex_left, tz_str)
    if match_result_right is not None:
        offset, tz_name = match_result_right.groups()[2], match_result_right.groups()[1]
    elif match_result_left is not None:
        offset, tz_name = match_result_left.groups()[1], match_result_left.groups()[2]

    if offset is None:  # TODO refactor this
        if "CEST" in tz_str or "CENTRALEUROPEANSUMMERTIME" in tz_str:
            offset, tz_name = 2, "CEST"
        if "EST" in tz_str or "EASTERNSTANDARDTIME" in tz_str:
            offset, tz_name = 0, "EST"
        if "CST" in tz_str or "CENTRALSTANDARDTIME" in tz_str:
            offset, tz_name = -6, "CST"
        if "CET" in tz_str or "CENTRALEUROPEANTIME" in tz_str:
            offset, tz_name = 1, "CET"
        if "UTC" in tz_str or "COORDINATEDUNIVERSALTIME" in tz_str:
            offset, tz_name = 0, "UTC"
        if "GMT" in tz_str or "GREENWICHMEANTIME" in tz_str:
            offset, tz_name = 0, "GMT"

    if offset is not None and tz_name is not None:
        offset = int(offset)
        sign = -1 if offset < 0 else 1
        return datetime.timezone(sign * datetime.timedelta(hours=abs(offset)), name=tz_name)

    tz_name = _city_to_timezone(tz_str)
    if tz_name is not None:
        return pytz.timezone(tz_name)
    return None


def find_any_email(email_str: str) -> str | None:
    regex = re.compile(
        r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])"  # noqa: E501
    )
    match = re.search(regex, email_str)
    if match is not None:
        return match.group(0)
    return None


def parse_email(email_str: str) -> str | None:
    email_str = email_str.strip().rstrip()
    emails_to_test = []
    emails_to_test.append(email_str)
    emails_to_test.append(find_any_email(email_str) or "")
    for email in emails_to_test:
        try:
            validate_email(email_str)
            return email
        except EmailNotValidError:
            pass
    raise ValueError(f"email: {email_str} is not valid")


def parse_telegram_name(tg_str: str) -> str | None:
    tg_str = tg_str.strip()

    # usernames
    tg_regex = re.compile(r"@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*")
    match_result = re.search(tg_regex, tg_str)
    if match_result is not None:
        return match_result.group(0)

    # http links
    tg_http_regex = re.compile(r"/t.me/(\w{5,32}\b)")
    match_result = re.search(tg_http_regex, tg_str)
    if match_result is not None:
        return f"@{match_result.group(1)}"

    # just a name
    tg_http_regex = re.compile(r"\w{5,32}\b")
    match_result = re.match(tg_http_regex, tg_str)
    if match_result is not None and len(match_result.group(0)) == len(tg_str):
        return f"@{match_result.group(0)}"

    return None


def find_any_phone_number(number_str: str) -> list[str]:
    number_str = number_str.replace(" ", "")
    regex = re.compile(r"\+?(?:\d{1,3}[-\s\.]?)?(?:\(\d{1,4}\))?[0-9]{3,5}[-\s\.]?[0-9]{3,5}")
    return re.findall(regex, number_str)


def parse_phone_number(number_str: str) -> str | None:
    number_str = number_str.replace(" ", "")
    country_codes_to_test = [("", None)] + [
        (f"+{code}", region[0])
        for code, region in phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items()
    ]

    phone_numbers = find_any_phone_number(number_str)
    phone_numbers.append(number_str)

    # handle different rare cases
    if number_str and number_str[0] == "0":
        phone_numbers.append(number_str[1:])
    if number_str and number_str[0] != "+":
        phone_numbers.append("+" + number_str)
    if number_str and number_str[0:2] == "+8":
        phone_numbers.append("+3" + number_str[1:])
    if number_str and number_str[0:2] == "00":
        phone_numbers.append("+" + number_str[2:])

    is_can_be_parsed = False
    parsed_number = None
    for raw_phone_number in phone_numbers:
        if parsed_number is not None:
            break
        for country_code, region in country_codes_to_test:
            number_to_parse = country_code + raw_phone_number
            try:
                _result = phonenumbers.parse(number_to_parse, region=region)
                is_can_be_parsed = True
                if phonenumbers.is_valid_number(_result):
                    parsed_number = _result
                    break
            except phonenumbers.NumberParseException:
                pass

    if parsed_number is None:
        message = "Can be parsed but invalid" if is_can_be_parsed else "Can not be parsed"
        raise ValueError(f"Phone {message}, phone number: {number_str}")

    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)


def parse_name(name_str: str) -> str:
    name_str = name_str.strip()
    if len(name_str) < MIN_NAME_LENGTH:
        raise ValueError(f"Name {name_str} is not valid")
    return name_str


def parse_language_level(level_str: str) -> list[str]:
    language_levels = [e.value for e in LanguageLevelId]
    if "any" in level_str.lower() or "любой" in level_str.lower():
        return language_levels

    # sometimes people use russian
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
    slot_str = slot_str.lower().strip().rstrip()
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
