from datetime import timedelta


class AlertConfig:
    PERIODS = {
        "TWO_WEEKS": timedelta(weeks=2),
        "ONE_MONTH": timedelta(days=30),
        # TODO: добавить другие периоды по необходимости
    }

    TYPES = {
        "OVERDUE_ON_LEAVE": "overdue_on_leave",
        "LOW_STUDENT_ACTIVITY": "low_student_activity",
        # TODO: добавить другие типы алертов здесь
    }
