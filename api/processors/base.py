from abc import ABC
from datetime import datetime

import pytz

from api.models.choices.statuses import Status
from api.models.groups import Group
from api.models.people import Person


class Processor(ABC):
    @staticmethod
    def _set_status(obj: Group | Person, status: Status) -> None:
        """Sets status, sets `status_since` to current time in UTC, saves object."""
        obj.status = status
        obj.status_since = datetime.now(tz=pytz.UTC)
        obj.save()
