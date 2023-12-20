import contextlib
import datetime
import re

import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


def _city_to_timezone(city_name: str) -> str | None:
    geolocator = Nominatim(user_agent="city-to-timezone")
    coords = geolocator.geocode(city_name)
    tf = TimezoneFinder()
    if coords:
        return tf.timezone_at(lng=coords.longitude, lat=coords.latitude)

    return None


def parse_timezone(tz: str) -> datetime.tzinfo | None:
    tz_str = str(tz)
    tz_name = None
    offset = None
    regex_right = r"((UTC|GMT)([\+|\-]\d*))"
    regex_left = r"(([\+|\-]\d*)(UTC|GMT))"
    tz_str = str(tz).replace(" ", "").upper()

    match_result_right = re.findall(regex_right, tz_str)
    match_result_left = re.findall(regex_left, tz_str)
    if len(match_result_right) > 0:
        offset, tz_name = match_result_right[0][2], match_result_right[0][1]
    elif len(match_result_left) > 0:
        offset, tz_name = match_result_left[0][1], match_result_left[0][2]

    if offset is None:
        if "CET" in tz_str or "CEST" in tz_str:
            offset, tz_name = 2, "CET"
        if "EST" in tz_str or "EASTERNSTANDARDTIME" in tz_str:
            offset, tz_name = 0, "EST"
        if "CST" in tz_str or "CENTRALSTANDARDTIME" in tz_str:
            offset, tz_name = -6, "CST"
        if "CET" in tz_str or "CENTRALEUROPEANTIME" in tz_str:
            offset, tz_name = 1, "CET"
        if "UTC" in tz_str or "COORDINATEDUNIVERSALTIME" in tz_str:
            offset, tz_name = 0, "UTC"
        if "GMT" in tz_str or "GreenwichMeanTimeZone".upper() in tz_str:
            offset, tz_name = 0, "GMT"

    if offset is not None and tz_name is not None:
        offset = int(offset)
        sign = -1 if offset < 0 else 1
        return datetime.timezone(sign * datetime.timedelta(hours=abs(offset)), name=tz_name)

    with contextlib.suppress(Exception):
        tz_name = _city_to_timezone(tz_str)
        if tz_name is not None:
            return pytz.timezone(tz_name)
    return None  # or return default "UTC"?
