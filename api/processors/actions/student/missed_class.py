from datetime import timedelta

from django.db import transaction

from api.models import Group, Student
from api.models.auxil.constants import STUDENT_CLASS_MISS_LIMIT
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status import StudentSituationalStatus
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentMissedClassProcessor(StudentActionProcessor):
    def __init__(self, student: Student, group: Group, notified: bool):
        self.notified = notified
        self.group = group
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._create_log_events()
        self._set_statuses()

    def _is_student_reached_limit(self) -> bool:
        last_two_weeks_date = self.timestamp - timedelta(weeks=2)
        student_class_misses_count = StudentLogEvent.objects.filter(
            date_time__gte=last_two_weeks_date,
            type=StudentLogEventType.MISSED_CLASS_SILENTLY,
            student=self.student,
        ).count()
        return student_class_misses_count >= STUDENT_CLASS_MISS_LIMIT

    def _set_statuses(self) -> None:
        if self._is_student_reached_limit():
            self.student.situational_status = StudentSituationalStatus.NOT_ATTENDING
            self.student.status_since = self.timestamp
            self.student.save()

    def _create_log_events(self) -> None:
        event_type = (
            StudentLogEventType.MISSED_CLASS_NOTIFIED if self.notified else StudentLogEventType.MISSED_CLASS_SILENTLY
        )
        StudentLogEvent.objects.create(
            student=self.student, from_group=self.group, to_group=self.group, type=event_type
        )
