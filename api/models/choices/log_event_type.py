from django.db import models
from django.utils.translation import gettext_lazy as _


class CoordinatorLogEventType(models.TextChoices):
    APPLIED = "applied", _("Applied for the role")
    JOINED = "joined", _("Joined the common group")
    TOOK_NEW_GROUP = (
        "took_new_group",
        _("Took a new group (not transferred from another coordinator)"),
    )
    GROUP_STARTED_CLASSES = "group_started_classes", _("The group started classes")
    REQUESTED_TRANSFER = (
        "requested_transfer",
        _("Requested that the group be transferred to a different coordinator"),
    )
    TRANSFER_CANCELED = (
        "transfer_canceled",
        _("Transfer canceled (declined or the coordinator changed their mind)"),
    )
    TRANSFER_COMPLETED = "transferred", _("Transfer of group to another coordinator completed")
    TOOK_TRANSFERRED_GROUP = "took_transfer", _("Received group from another coordinator")
    GONE_ON_LEAVE = "gone_on_leave", _("Gone on leave")
    RETURNED_FROM_LEAVE = "returned_from_leave", _("Returned from leave")
    LEFT_PREMATURELY = "left_prematurely", _("Left the project prematurely")
    FINISHED_AND_LEAVING = (
        "finished_and_leaving",
        _("Finished working and announced that they are leaving the project"),
    )
    FINISHED_AND_STAYING = (
        "finished_and_staying",
        _("Finished working and announced that they are staying in the project"),
    )
    EXPELLED = "expelled", _("Expelled from the project")
    ACCESS_REVOKED = "access_revoked", _("Access to corporate resources revoked")
    GROUP_ABORTED = "group_aborted", _("Group finished prematurely")
    GROUP_FINISHED = "group_finished", _("Group studies are finished")
    ADDED_STUDENT_TO_EXISTING_GROUP = (
        "added_student_to_existing group",
        _("Added student to a group that was already studying"),
    )


COORDINATOR_LOG_EVENTS_REQUIRE_GROUP = [
    CoordinatorLogEventType.TOOK_NEW_GROUP,
    CoordinatorLogEventType.GROUP_STARTED_CLASSES,
    CoordinatorLogEventType.TOOK_TRANSFERRED_GROUP,
    CoordinatorLogEventType.REQUESTED_TRANSFER,
    CoordinatorLogEventType.TRANSFER_CANCELED,
    CoordinatorLogEventType.TRANSFER_COMPLETED,
    CoordinatorLogEventType.GROUP_ABORTED,
    CoordinatorLogEventType.GROUP_FINISHED,
]


class GroupLogEventType(models.TextChoices):
    FORMED = "formed", _("Formed (automatically or by coordinator)")
    CONFIRMED = "confirmed", _("Confirmed")
    STARTED = "started", _("Started classes")
    ABORTED = "aborted", _("Finished prematurely")
    FINISHED = "finished", _("Finished successfully")
    COORDINATOR_REQUESTED_TRANSFER = (
        "coordinator_requested_transfer",
        _("Coordinator requested transfer of group to another coordinator"),
    )
    STUDENT_REQUESTED_TRANSFER = (
        "student_requested_transfer",
        _("Student requested transfer to another group"),
    )
    TEACHER_REQUESTED_SUBSTITUTION = (
        "teacher_requested_substitution",
        _("Teacher requested to be substituted with another teacher"),
    )


class StudentLogEventType(models.TextChoices):
    REGISTERED = "registered", _("Completed registration")
    AWAITING_OFFER = "awaiting_offer", _("Registration complete, waiting for a group")
    GROUP_OFFERED = "group_offered", _("Was offered a group, has not responded yet")
    ACCEPTED_OFFER = "accepted_offer", _("Was offered a group and accepted it")
    DECLINED_OFFER = "declined_offer", _("Was offered a group but declined it")
    TENTATIVE_GROUP_DISCARDED = (
        "tentative_group_discarded",
        _("Tentative group was discarded for reasons other than the person's own decision"),
    )
    GROUP_CONFIRMED = "group_confirmed", _("Group confirmed, awaiting start of classes")
    STUDY_START = "start", _("Started studying in a group")
    MISSED_CLASS_NOTIFIED = (
        "missed_class_notified",
        _("Missed a class but let the teacher know in advance"),
    )
    MISSED_CLASS_SILENTLY = (
        "missed_class_silently",
        _("Missed a class without letting the teacher know in advance"),
    )
    REQUESTED_TRANSFER = "requested_transfer", _("Requested transfer")
    TRANSFERRED = "transferred", _("Transferred")
    TRANSFER_CANCELED = "transfer_canceled", _("Transfer canceled")
    LEFT_PREMATURELY = "left_prematurely", _("Left the project prematurely")
    EXPELLED = "expelled", _("Expelled from the project")
    FINISHED_AND_LEAVING = "finished_left", _("Completed the course and left the project")
    GROUP_ABORTED = "group_aborted", _("Group finished prematurely")
    GROUP_FINISHED = "group_finished", _("Group finished successfully")
    GONE_ON_LEAVE = "gone_on_leave", _("Gone on leave")
    RETURNED_FROM_LEAVE = "returned_from_leave", _("Returned from leave")


class TeacherLogEventType(models.TextChoices):
    REGISTERED = "registered", _("Completed registration")
    AWAITING_OFFER = (
        "awaiting_offer",
        _("Registration and validation complete, started waiting for a group"),
    )
    GROUP_OFFERED = "group_offered", _("Was offered a group, has not responded yet")
    ACCEPTED_OFFER = "accepted_offer", _("Was offered a group and accepted it")
    VALIDATED = "validated", _("Validated in a face-to-face interview")
    DECLINED_OFFER = "declined_offer", _("Was offered a group but declined it")
    TENTATIVE_GROUP_DISCARDED = (
        "tentative_group_discarded",
        _("Tentative group was discarded for reasons other than the person's own decision"),
    )
    GROUP_CONFIRMED = "group_confirmed", _("Group confirmed, awaiting start of classes")
    STUDY_START = "started_teaching_group", _("Started teaching a group")
    HOSTED_SPEAKING_CLUB = "hosted_speaking_club", _("Hosted a speaking club session")
    REQUESTED_TRANSFER = "requested_transfer", _("Requested transfer")
    TRANSFERRED = "transferred", _("Transferred")
    TRANSFER_CANCELED = "transfer_canceled", _("Transfer canceled")
    LEFT_PREMATURELY = "left_prematurely", _("Left the project prematurely")
    FINISHED_AND_LEAVING = (
        "finished_and_leaving",
        _("Finished working and announced that they are leaving the project"),
    )
    FINISHED_AND_STAYING = (
        "finished_and_staying",
        _("Finished working and announced that they are staying in the project"),
    )
    EXPELLED = "expelled", _("Expelled from the project")
    ACCESS_REVOKED = "access_revoked", _("Access to corporate resources revoked")
    GROUP_ABORTED = "group_aborted", _("Group finished prematurely")
    GROUP_FINISHED = "group_finished", _("Group finished successfully")
    GONE_ON_LEAVE = "gone_on_leave", _("Gone on leave")
    RETURNED_FROM_LEAVE = "returned_from_leave", _("Returned from leave")


class TeacherUnder18LogEventType(models.TextChoices):
    REGISTERED = "registered", _("Completed registration")
    VALIDATED = "validated", _("Validated in a face-to-face interview")
    HOSTED_SPEAKING_CLUB = "hosted_speaking_club", _("Hosted a speaking club session")
    LEFT = "left", _("Left the project")
    EXPELLED = "expelled", _("Expelled from the project")
    ACCESS_REVOKED = "access_revoked", _("Access to corporate resources revoked")
    GONE_ON_LEAVE = "gone_on_leave", _("Gone on leave")
    RETURNED_FROM_LEAVE = "returned_from_leave", _("Returned from leave")
