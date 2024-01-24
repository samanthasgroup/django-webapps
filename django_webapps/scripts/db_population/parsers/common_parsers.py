import datetime
import re

import pytz
from email_validator import EmailNotValidError, validate_email
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


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


def parse_email(email_str: str) -> str | None:
    email_str = email_str.strip()
    try:
        validate_email(email_str)
    except EmailNotValidError:
        raise ValueError(f"email: {email_str} is not valid")
    return email_str


def parse_telegram_name(tg_str: str) -> str | None:
    tg_str = tg_str.strip()
    tg_regex = re.compile(r"@(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*")
    match_result = re.search(tg_regex, tg_str)
    if match_result is not None:
        return match_result.group(0)
    raise ValueError(f"tg: {tg_str} is not valid")
