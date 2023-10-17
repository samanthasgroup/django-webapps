from django.db import models


class CoordinatorLogEventType(models.TextChoices):
    APPLIED = "applied", "Applied for the role"
    JOINED = "joined", "Joined the common group"
    STARTED_ONBOARDING = "onboarding_start", "Joined the onboarding group"
    TOOK_NEW_GROUP = (
        "took_new_group",
        "Took a new group (not transferred from another coordinator)",
    )
    GROUP_STARTED_CLASSES = "group_started_classes", "The group started classes"
    REQUESTED_TRANSFER = (
        "requested_transfer",
        "Requested that the group be transferred to a different coordinator",
    )
    TRANSFER_CANCELED = (
        "transfer_canceled",
        "Transfer canceled (declined or the coordinator changed their mind)",
    )
    TRANSFER_COMPLETED = "transferred", "Transfer of group to another coordinator completed"
    TOOK_TRANSFERRED_GROUP = "took_transfer", "Received group from another coordinator"
    GONE_ON_LEAVE = "gone_on_leave", "Gone on leave"
    RETURNED_FROM_LEAVE = "returned_from_leave", "Returned from leave"
    LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
    FINISHED_AND_LEAVING = (
        "finished_and_leaving",
        "Finished working and announced that they are leaving the project",
    )
    FINISHED_AND_STAYING = (
        "finished_and_staying",
        "Finished working and announced that they are staying in the project",
    )
    EXPELLED = "expelled", "Expelled from the project"
    ACCESS_REVOKED = "access_revoked", "Access to corporate resources revoked"
    GROUP_ABORTED = "group_aborted", "Group finished prematurely"
    GROUP_FINISHED = "group_finished", "Group studies are finished"
    ADDED_STUDENT_TO_EXISTING_GROUP = (
        "added_student_to_existing group",
        "Added student to a group that was already studying",
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
    FORMED = "formed", "Formed (automatically or by coordinator)"
    CONFIRMED = "confirmed", "Confirmed"
    STARTED = "started", "Started classes"
    ABORTED = "aborted", "Finished prematurely"
    FINISHED = "finished", "Finished successfully"
    COORDINATOR_REQUESTED_TRANSFER = (
        "coordinator_requested_transfer",
        "Coordinator requested transfer of group to another coordinator",
    )
    STUDENT_REQUESTED_TRANSFER = (
        "student_requested_transfer",
        "Student requested transfer to another group",
    )
    TEACHER_REQUESTED_SUBSTITUTION = (
        "teacher_requested_substitution",
        "Teacher requested to be substituted with another teacher",
    )


class StudentLogEventType(models.TextChoices):
    REGISTERED = "registered", "Completed registration"
    AWAITING_OFFER = "awaiting_offer", "Registration complete, waiting for a group"
    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    ACCEPTED_OFFER = "accepted_offer", "Was offered a group and accepted it"
    DECLINED_OFFER = "declined_offer", "Was offered a group but declined it"
    TENTATIVE_GROUP_DISCARDED = (
        "tentative_group_discarded",
        "Tentative group was discarded for reasons other than the person's own decision",
    )
    GROUP_CONFIRMED = "group_confirmed", "Group confirmed, awaiting start of classes"
    STUDY_START = "start", "Started studying in a group"
    MISSED_CLASS_NOTIFIED = (
        "missed_class_notified",
        "Missed a class but let the teacher know in advance",
    )
    MISSED_CLASS_SILENTLY = (
        "missed_class_silently",
        "Missed a class without letting the teacher know in advance",
    )
    REQUESTED_TRANSFER = "requested_transfer", "Requested transfer"
    TRANSFERRED = "transferred", "Transferred"
    TRANSFER_CANCELED = "transfer_canceled", "Transfer canceled"
    LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
    EXPELLED = "expelled", "Expelled from the project"
    FINISHED_AND_LEAVING = "finished_left", "Completed the course and left the project"
    GROUP_ABORTED = "group_aborted", "Group finished prematurely"
    GROUP_FINISHED = "group_finished", "Group finished successfully"
    GONE_ON_LEAVE = "gone_on_leave", "Gone on leave"
    RETURNED_FROM_LEAVE = "returned_from_leave", "Returned from leave"


class TeacherLogEventType(models.TextChoices):
    REGISTERED = "registered", "Completed registration"
    AWAITING_OFFER = (
        "awaiting_offer",
        "Registration and validation complete, started waiting for a group",
    )
    GROUP_OFFERED = "group_offered", "Was offered a group, has not responded yet"
    ACCEPTED_OFFER = "accepted_offer", "Was offered a group and accepted it"
    VALIDATED = "Validated in a face-to-face interview"
    DECLINED_OFFER = "declined_offer", "Was offered a group but declined it"
    TENTATIVE_GROUP_DISCARDED = (
        "tentative_group_discarded",
        "Tentative group was discarded for reasons other than the person's own decision",
    )
    GROUP_CONFIRMED = "group_confirmed", "Group confirmed, awaiting start of classes"
    STUDY_START = "started_teaching_group", "Started teaching a group"
    HOSTED_SPEAKING_CLUB = "hosted_speaking_club", "Hosted a speaking club session"
    REQUESTED_TRANSFER = "requested_transfer", "Requested transfer"
    TRANSFERRED = "transferred", "Transferred"
    TRANSFER_CANCELED = "transfer_canceled", "Transfer canceled"
    LEFT_PREMATURELY = "left_prematurely", "Left the project prematurely"
    FINISHED_AND_LEAVING = (
        "finished_and_leaving",
        "Finished working and announced that they are leaving the project",
    )
    FINISHED_AND_STAYING = (
        "finished_and_staying",
        "Finished working and announced that they are staying in the project",
    )
    EXPELLED = "expelled", "Expelled from the project"
    ACCESS_REVOKED = "access_revoked", "Access to corporate resources revoked"
    GROUP_ABORTED = "group_aborted", "Group finished prematurely"
    GROUP_FINISHED = "group_finished", "Group finished successfully"
    GONE_ON_LEAVE = "gone_on_leave", "Gone on leave"
    RETURNED_FROM_LEAVE = "returned_from_leave", "Returned from leave"


class TeacherUnder18LogEventType(models.TextChoices):
    REGISTERED = "registered", "Completed registration"
    VALIDATED = "Validated in a face-to-face interview"
    HOSTED_SPEAKING_CLUB = "hosted_speaking_club", "Hosted a speaking club session"
    LEFT = "left", "Left the project"
    EXPELLED = "expelled", "Expelled from the project"
    ACCESS_REVOKED = "access_revoked", "Access to corporate resources revoked"
    GONE_ON_LEAVE = "gone_on_leave", "Gone on leave"
    RETURNED_FROM_LEAVE = "returned_from_leave", "Returned from leave"
