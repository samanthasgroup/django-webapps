from datetime import timedelta


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
        # TODO: добавить другие типы алертов здесь
    }

    STYLES = {
        "overdue_on_leave": "background: #fdecea; color: #a94442;",
        "overdue_transfer_request": "background: #ffe8d1; color: #8a3b12;",
        "coordinator_onboarding_stale": "background: #fff3cd; color: #856404;",
        "low_student_activity": "background: #fcf8e3; color: #8a6d3b;",
        "teacher_no_group_45_days": "background: #fff3cd; color: #856404;",
        "teacher_overdue_on_leave": "background: #fdecea; color: #a94442;",
        "teacher_overdue_group_offer": "background: #ffe8d1; color: #8a3b12;",
    }
