from abc import ABC
from datetime import datetime

import pytz

from api.models.choices.statuses import Status
from api.models.groups import Group
from api.models.people import Person


class Processor(ABC):
    @staticmethod
    def _set_status(
        obj: Group | Person, status: Status, status_since: datetime | None = None
    ) -> None:
        """Sets status, sets `status_since` to current time in UTC, saves object.

        Optionally, pass a datetime object as `status_since` to have identical timestamps
        for multiple log events.
        """
        obj.status = status
        obj.status_since = status_since or datetime.now(tz=pytz.UTC)
        obj.save()
