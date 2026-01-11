import datetime

from django.db import models
from django.utils import timezone

from api.models import Coordinator, Group, Student, Teacher
from api.models.choices.status import (
    CoordinatorProjectStatus,
    GroupProjectStatus,
    GroupSituationalStatus,
    ProjectStatus,
    SituationalStatus,
    StudentSituationalStatus,
    TeacherSituationalStatus,
)
from api.models.shared_abstract.person import Person


class StatusSetter:
    _TEACHER_HIGH_PRIORITY = {
        TeacherSituationalStatus.NEEDS_SUBSTITUTION,
        TeacherSituationalStatus.NO_RESPONSE,
    }
    _STUDENT_HIGH_PRIORITY = {
        StudentSituationalStatus.NEEDS_TRANSFER,
        StudentSituationalStatus.NOT_ATTENDING,
        StudentSituationalStatus.NO_RESPONSE,
    }

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
        coordinators = Coordinator.objects.filter_active()

        coordinators.filter_below_threshold().update(
            project_status=CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD, status_since=timestamp
        )
        coordinators.filter_above_threshold_and_within_limit().update(
            project_status=CoordinatorProjectStatus.WORKING_OK, status_since=timestamp
        )
        coordinators.filter_limit_reached().update(
            project_status=CoordinatorProjectStatus.WORKING_LIMIT_REACHED, status_since=timestamp
        )

    @classmethod
    def update_related_statuses_for_group(cls, group: Group, timestamp: datetime.datetime) -> None:
        cls.update_related_statuses_for_people(
            teachers=group.teachers.all(),
            students=group.students.all(),
            timestamp=timestamp,
        )

    @classmethod
    def update_related_statuses_for_people(
        cls, *, teachers: "models.QuerySet[Teacher]", students: "models.QuerySet[Student]", timestamp: datetime.datetime
    ) -> None:
        cls._recalculate_teacher_situational_statuses(teachers, timestamp)
        cls._recalculate_student_situational_statuses(students, timestamp)

    @classmethod
    def _recalculate_teacher_situational_statuses(
        cls, teachers: "models.QuerySet[Teacher]", timestamp: datetime.datetime
    ) -> None:
        teachers = teachers.prefetch_related("groups")
        updates: dict[TeacherSituationalStatus | str, list[int]] = {}

        for teacher in teachers:
            current = teacher.situational_status or ""
            if current in cls._TEACHER_HIGH_PRIORITY:
                new_status: TeacherSituationalStatus | str = current
            else:
                groups = list(teacher.groups.all())
                has_holiday = any(g.situational_status == GroupSituationalStatus.HOLIDAY for g in groups)
                has_awaiting_start = any(g.project_status == GroupProjectStatus.AWAITING_START for g in groups)
                has_pending = any(g.project_status == GroupProjectStatus.PENDING for g in groups)
                if has_holiday:
                    new_status = TeacherSituationalStatus.HOLIDAY
                elif has_awaiting_start:
                    new_status = TeacherSituationalStatus.AWAITING_START
                elif has_pending:
                    new_status = TeacherSituationalStatus.GROUP_OFFERED
                else:
                    new_status = ""

            if new_status != current:
                updates.setdefault(new_status, []).append(teacher.pk)

        for status_value, ids in updates.items():
            Teacher.objects.filter(pk__in=ids).update(situational_status=status_value, status_since=timestamp)

    @classmethod
    def _recalculate_student_situational_statuses(
        cls, students: "models.QuerySet[Student]", timestamp: datetime.datetime
    ) -> None:
        students = students.prefetch_related("groups")
        updates: dict[StudentSituationalStatus | str, list[int]] = {}

        for student in students:
            current = student.situational_status or ""
            if current in cls._STUDENT_HIGH_PRIORITY:
                new_status: StudentSituationalStatus | str = current
            else:
                groups = list(student.groups.all())
                has_holiday = any(g.situational_status == GroupSituationalStatus.HOLIDAY for g in groups)
                has_awaiting_start = any(g.project_status == GroupProjectStatus.AWAITING_START for g in groups)
                if has_holiday:
                    new_status = StudentSituationalStatus.HOLIDAY
                elif has_awaiting_start:
                    new_status = StudentSituationalStatus.AWAITING_START
                elif current == StudentSituationalStatus.GROUP_OFFERED and groups:
                    new_status = StudentSituationalStatus.GROUP_OFFERED
                else:
                    new_status = ""

            if new_status != current:
                updates.setdefault(new_status, []).append(student.pk)

        for status_value, ids in updates.items():
            Student.objects.filter(pk__in=ids).update(situational_status=status_value, status_since=timestamp)
