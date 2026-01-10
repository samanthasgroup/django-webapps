from datetime import timedelta

from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _


class AlertConfig:
    PERIODS = {
        "TWO_WEEKS": timedelta(weeks=2),
        "ONE_MONTH": timedelta(days=30),
        "FORTY_FIVE_DAYS": timedelta(days=45),
        # TODO: добавить другие периоды по необходимости
    }

    TYPES = {
        "OVERDUE_ON_LEAVE": "overdue_on_leave",
        "OVERDUE_TRANSFER_REQUEST": "overdue_transfer_request",
        "ONBOARDING_STALE": "coordinator_onboarding_stale",
        "LOW_STUDENT_ACTIVITY": "low_student_activity",
        "TEACHER_NO_GROUP_45_DAYS": "teacher_no_group_45_days",
        "TEACHER_OVERDUE_ON_LEAVE": "teacher_overdue_on_leave",
        "TEACHER_OVERDUE_GROUP_OFFER": "teacher_overdue_group_offer",
        "STUDENT_NEEDS_ORAL_INTERVIEW": "student_needs_oral_interview",
        "STUDENT_OVERDUE_GROUP_OFFER": "student_overdue_group_offer",
        "STUDENT_NO_GROUP_30_DAYS": "student_no_group_30_days",
        "GROUP_PENDING_OVERDUE": "group_pending_overdue",
        "GROUP_AWAITING_START_OVERDUE": "group_awaiting_start_overdue",
        # TODO: добавить другие типы алертов здесь
    }

    LABELS = {
        TYPES["OVERDUE_ON_LEAVE"]: _("Overdue on leave"),
        TYPES["OVERDUE_TRANSFER_REQUEST"]: _("Overdue transfer request"),
        TYPES["ONBOARDING_STALE"]: _("Onboarding stale"),
        TYPES["LOW_STUDENT_ACTIVITY"]: _("Low student activity"),
        TYPES["TEACHER_NO_GROUP_45_DAYS"]: _("Teacher without group for 45 days"),
        TYPES["TEACHER_OVERDUE_ON_LEAVE"]: _("Teacher overdue on leave"),
        TYPES["TEACHER_OVERDUE_GROUP_OFFER"]: _("Teacher overdue group offer"),
        TYPES["STUDENT_NEEDS_ORAL_INTERVIEW"]: _("Student needs oral interview"),
        TYPES["STUDENT_OVERDUE_GROUP_OFFER"]: _("Student overdue group offer"),
        TYPES["STUDENT_NO_GROUP_30_DAYS"]: _("Student without group for 30 days"),
        TYPES["GROUP_PENDING_OVERDUE"]: _("Group pending overdue"),
        TYPES["GROUP_AWAITING_START_OVERDUE"]: _("Group awaiting start overdue"),
    }

    STYLES = {
        "overdue_on_leave": "background: #fdecea; color: #a94442;",
        "overdue_transfer_request": "background: #ffe8d1; color: #8a3b12;",
        "coordinator_onboarding_stale": "background: #fff3cd; color: #856404;",
        "low_student_activity": "background: #fcf8e3; color: #8a6d3b;",
        "teacher_no_group_45_days": "background: #fff3cd; color: #856404;",
        "teacher_overdue_on_leave": "background: #fdecea; color: #a94442;",
        "teacher_overdue_group_offer": "background: #ffe8d1; color: #8a3b12;",
        "student_needs_oral_interview": "background: #fff3cd; color: #856404;",
        "student_overdue_group_offer": "background: #ffe8d1; color: #8a3b12;",
        "student_no_group_30_days": "background: #fff3cd; color: #856404;",
        "group_pending_overdue": "background: #f2f2f2; color: #555555;",
        "group_awaiting_start_overdue": "background: #fff3cd; color: #856404;",
    }

    @classmethod
    def choices(cls) -> list[tuple[str, str | Promise]]:
        return [(alert_type, cls.LABELS.get(alert_type, alert_type)) for alert_type in cls.TYPES.values()]
