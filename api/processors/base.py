import datetime
from abc import ABC

from django.utils import timezone

from api.models.choices.status import Status
from api.models.group import Group
from api.models.shared_abstract.person import Person


class Processor(ABC):
    @staticmethod
    def _set_status(
        obj: Group | Person, status: Status, status_since: datetime.datetime | None = None
    ) -> None:
        """Sets status, sets `status_since` to current time in UTC, saves object.

        Optionally, pass a datetime object as `status_since` to have identical timestamps
        for multiple log events.
        """
        obj.status = status
        obj.status_since = status_since or timezone.now()
        obj.save()