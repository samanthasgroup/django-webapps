from django.db import transaction
from django.db.models import Count

from api.models import Group, Student, Teacher
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.log_event_type import StudentLogEventType, TeacherLogEventType
from api.models.choices.status import StudentProjectStatus, TeacherProjectStatus
from api.processors.actions.group import GroupActionProcessor
from api.processors.auxil.log_event_creator import GroupLogEventCreator


class GroupDiscardProcessor(GroupActionProcessor):
    def __init__(self, group: Group, reason: str):
        self.reason = reason
        super().__init__(group)

    @transaction.atomic
    def process(self) -> None:
        teachers = list(self.group.teachers.all())
        students = list(self.group.students.all())
        coordinators = list(self.group.coordinators.all())

        self._set_statuses()
        self._create_log_events()
        self._delete()

        timestamp = self.timestamp
        if coordinators:
            StatusSetter.update_statuses_of_active_coordinators(timestamp)
        if teachers or students:
            StatusSetter.update_related_statuses_for_people(
                teachers=Teacher.objects.filter(pk__in=[t.pk for t in teachers]),
                students=Student.objects.filter(pk__in=[s.pk for s in students]),
                timestamp=timestamp,
            )

    def _create_log_events(self) -> None:
        # TODO add from_groupd once CASCAD policy removed
        GroupLogEventCreator.create(
            group=self.group,
            student_log_event_type=StudentLogEventType.TENTATIVE_GROUP_DISCARDED,
            teacher_log_event_type=TeacherLogEventType.TENTATIVE_GROUP_DISCARDED,
            comment=self.reason,
        )

    def _delete(self) -> None:
        self.group.delete()

    def _set_group_status(self) -> None:
        pass

    def _set_coordinators_status(self) -> None:
        StatusSetter.update_statuses_of_active_coordinators(self.timestamp)

    def _set_teachers_status(self) -> None:
        self.group.teachers_with_other_groups().update(
            project_status=TeacherProjectStatus.WORKING,
            status_since=self.timestamp,
        )

        self.group.teachers_with_no_other_groups().update(
            project_status=TeacherProjectStatus.NO_GROUP_YET,
            status_since=self.timestamp,
        )

    def _set_students_status(self) -> None:
        annotated_students = Student.objects.annotate(groups_count=Count("groups")).filter(groups=self.group)

        annotated_students.filter(groups_count__gt=1).update(
            project_status=StudentProjectStatus.STUDYING,
            status_since=self.timestamp,
        )

        annotated_students.filter(groups_count=1).update(
            project_status=StudentProjectStatus.NO_GROUP_YET,
            status_since=self.timestamp,
        )
