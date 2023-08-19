import datetime

from django.utils import timezone

from api.models import Coordinator, Group
from api.models.choices.status import CoordinatorProjectStatus, ProjectStatus, SituationalStatus
from api.models.shared_abstract.person import Person


class StatusSetter:
    @staticmethod
    def set_status(
        obj: Group | Person,
        project_status: ProjectStatus | None = None,
        situational_status: SituationalStatus | None = None,
        status_since: datetime.datetime | None = None,
    ) -> None:
        """Set statuses, `status_since` to given time or current time in UTC, save object.

        Note:
            Pass a datetime object as `status_since` to have identical timestamps
            for multiple log events.
        """
        if project_status:
            obj.project_status = project_status
        if situational_status:
            obj.situational_status = situational_status
        obj.status_since = status_since or timezone.now()
        obj.save()

    @staticmethod
    def update_statuses_of_active_coordinators(timestamp: datetime.datetime) -> None:
        coordinators = Coordinator.objects.filter_active()  # type: ignore[attr-defined]

        coordinators.filter_below_threshold().update(
            project_status=CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.filter_above_threshold_and_within_limit().update(
            project_status=CoordinatorProjectStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.filter_limit_reached().update(
            project_status=CoordinatorProjectStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )
