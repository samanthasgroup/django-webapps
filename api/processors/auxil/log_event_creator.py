from django.db import transaction

from api.models import (
    Coordinator,
    CoordinatorLogEvent,
    Group,
    GroupLogEvent,
    StudentLogEvent,
    TeacherLogEvent,
)
from api.models.auxil.constants import CoordinatorGroupLimit
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    GroupLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import CoordinatorProjectStatus, CoordinatorSituationalStatus
from api.models.choices.status.situational import CoordinatorSituationalStatusOrEmpty


class GroupLogEventCreator:
    @staticmethod
    def create(  # noqa: PLR0913
        group: Group,
        student_log_event_type: StudentLogEventType,
        teacher_log_event_type: TeacherLogEventType,
        group_log_event_type: GroupLogEventType | None = None,
        coordinator_log_event_type: CoordinatorLogEventType | None = None,
        from_group: Group | None = None,
        to_group: Group | None = None,
        comment: str = "",
    ) -> None:
        if group_log_event_type is not None:
            GroupLogEvent.objects.create(group=group, type=group_log_event_type, comment=comment)
        if coordinator_log_event_type is not None:
            CoordinatorLogEvent.objects.bulk_create(
                CoordinatorLogEvent(
                    coordinator=coordinator,
                    group=group,
                    type=coordinator_log_event_type,
                    comment=comment,
                )
                for coordinator in group.coordinators.iterator()
            )
        StudentLogEvent.objects.bulk_create(
            StudentLogEvent(
                student=student,
                type=student_log_event_type,
                from_group=from_group,
                to_group=to_group,
                comment=comment,
            )
            for student in group.students.iterator()
        )

        TeacherLogEvent.objects.bulk_create(
            TeacherLogEvent(
                teacher=teacher,
                type=teacher_log_event_type,
                from_group=from_group,
                to_group=to_group,
                comment=comment,
            )
            for teacher in group.teachers.iterator()
        )


class CoordinatorAdminLogEventCreator:
    @staticmethod
    def _get_working_project_status(coordinator: Coordinator) -> CoordinatorProjectStatus:
        group_count = coordinator.groups.count()
        if group_count < CoordinatorGroupLimit.MIN:
            return CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD
        if CoordinatorGroupLimit.MIN <= group_count < CoordinatorGroupLimit.MAX:
            return CoordinatorProjectStatus.WORKING_OK
        if group_count >= CoordinatorGroupLimit.MAX:
            return CoordinatorProjectStatus.WORKING_LIMIT_REACHED

        raise NotImplementedError(
            f"Unexpected group count: {group_count}, coordinator: {coordinator}, "
            f"limits: {CoordinatorGroupLimit.MAX=}, {CoordinatorGroupLimit.MIN=}"
        )

    @classmethod
    def _get_statuses_by_event_type(  # noqa: PLR0911
        cls,
        coordinator: Coordinator,
        event_type: CoordinatorLogEventType,
    ) -> tuple[CoordinatorProjectStatus | None, CoordinatorSituationalStatusOrEmpty | None]:
        """Get statuses by event type.

        Returns project status and situational status
            which should be set for coordinator by event type.
        Returned None as status means that status should not be changed.
        """
        match event_type:
            case CoordinatorLogEventType.APPLIED | CoordinatorLogEventType.JOINED:
                return CoordinatorProjectStatus.PENDING, ""
            case CoordinatorLogEventType.STARTED_ONBOARDING:
                return (
                    CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD,
                    CoordinatorSituationalStatus.ONBOARDING,
                )
            case CoordinatorLogEventType.GONE_ON_LEAVE:
                return CoordinatorProjectStatus.ON_LEAVE, ""
            case CoordinatorLogEventType.LEFT_PREMATURELY:
                return CoordinatorProjectStatus.LEFT_PREMATURELY, ""
            case CoordinatorLogEventType.FINISHED_AND_LEAVING:
                return CoordinatorProjectStatus.FINISHED_LEFT, ""
            case CoordinatorLogEventType.FINISHED_AND_STAYING:
                return CoordinatorProjectStatus.FINISHED_STAYS, ""
            case CoordinatorLogEventType.EXPELLED:
                return CoordinatorProjectStatus.BANNED, ""
            case CoordinatorLogEventType.ACCESS_REVOKED:
                return CoordinatorProjectStatus.REMOVED, ""
            case (
                CoordinatorLogEventType.TRANSFER_COMPLETED
                | CoordinatorLogEventType.TOOK_TRANSFERRED_GROUP
                | CoordinatorLogEventType.RETURNED_FROM_LEAVE
                | CoordinatorLogEventType.GROUP_ABORTED
                | CoordinatorLogEventType.GROUP_FINISHED
                | CoordinatorLogEventType.TOOK_NEW_GROUP
                | CoordinatorLogEventType.GROUP_STARTED_CLASSES
            ):
                return cls._get_working_project_status(coordinator), ""
            case (
                CoordinatorLogEventType.REQUESTED_TRANSFER
                | CoordinatorLogEventType.TRANSFER_CANCELED
            ):
                return None, None

    @classmethod
    @transaction.atomic
    def create(
        cls,
        coordinator: Coordinator,
        log_event_type: CoordinatorLogEventType,
        comment: str = "",
    ) -> None:
        created_log_event = CoordinatorLogEvent.objects.create(
            coordinator=coordinator,
            type=log_event_type,
            comment=comment,
        )
        project_status, situational_status = cls._get_statuses_by_event_type(
            coordinator=coordinator,
            event_type=log_event_type,
        )

        # TODO: In future it could be a case when we need to set only one status
        if project_status is not None and situational_status is not None:
            StatusSetter.set_status(
                obj=coordinator,
                project_status=project_status,
                situational_status=situational_status,
                status_since=created_log_event.date_time,
            )
