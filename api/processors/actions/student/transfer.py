from django.db import transaction
from django.db.models import QuerySet

from api.models import Group, Student
from api.models.choices.log_event_type import StudentLogEventType
from api.models.choices.status.project import StudentProjectStatus
from api.models.log_event import StudentLogEvent
from api.processors.actions.student import StudentActionProcessor


class StudentTransferProcessor(StudentActionProcessor):
    def __init__(self, student: Student, to_group: Group):
        self.to_group = to_group
        super().__init__(student)

    @transaction.atomic
    def process(self) -> None:
        self._transfer()
        self._set_statuses()
        self._create_log_events()

    def _transfer(self) -> None:
        self.old_groups: QuerySet[Group] = self.student.groups.all()
        for old_group in self.old_groups:
            self.student.groups.remove(old_group)
            old_group.students_former.add(self.student)
            old_group.save()
        self.to_group.students.add(self.student)
        self.to_group.save()
        self.student.save()

    def _set_statuses(self) -> None:
        self.student.project_status = StudentProjectStatus.STUDYING
        self.student.situational_status = ""
        self.student.status_since = self.timestamp
        self.student.save()

    def _create_log_events(self) -> None:
        if self.old_groups:
            for old_group in self.old_groups:
                StudentLogEvent.objects.create(
                    student=self.student,
                    from_group=old_group,
                    to_group=self.to_group,
                    type=StudentLogEventType.TRANSFERRED,
                )
        else:
            StudentLogEvent.objects.create(
                student=self.student, to_group=self.to_group, type=StudentLogEventType.TRANSFERRED
            )
