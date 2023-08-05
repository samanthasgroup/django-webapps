import datetime

from django.utils import timezone

from api.models import Coordinator, Group
from api.models.choices.status import CoordinatorProjectStatus, ProjectStatus
from api.models.shared_abstract.person import Person


class StatusSetter:
    # FIXME situational status
    @staticmethod
    def set_status(
        obj: Group | Person,
        project_status: ProjectStatus,
        status_since: datetime.datetime | None = None,
    ) -> None:
        """Sets status, sets `status_since` to current time in UTC, saves object.

        Optionally, pass a datetime object as `status_since` to have identical timestamps
        for multiple log events.
        """
        obj.project_status = project_status
        obj.status_since = status_since or timezone.now()
        obj.save()

    @staticmethod
    def update_statuses_of_active_coordinators(timestamp: datetime.datetime) -> None:
        coordinators = Coordinator.objects

        coordinators.filter_below_threshold().update(
            status=CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.filter_above_threshold_and_within_limit().update(
            status=CoordinatorProjectStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.filter_limit_reached().update(
            status=CoordinatorProjectStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )
