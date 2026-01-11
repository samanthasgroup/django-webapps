import datetime

import pytest
from model_bakery import baker

from api.models import Group, Student, Teacher
from api.models.auxil.status_setter import StatusSetter
from api.models.choices.status import (
    GroupProjectStatus,
    GroupSituationalStatus,
    StudentProjectStatus,
    StudentSituationalStatus,
    TeacherProjectStatus,
    TeacherSituationalStatus,
)
from api.processors.actions.group.abort import GroupAbortProcessor
from api.processors.actions.group.confirm_ready_to_start import GroupConfirmReadyToStartProcessor
from api.processors.actions.group.create import GroupCreateProcessor


def _make_group(  # noqa: PLR0913
    *, availability_slots, timestamp, teachers, students, project_status, situational_status=""
) -> Group:
    group = baker.make(
        Group,
        _fill_optional=True,
        availability_slots_for_auto_matching=availability_slots,
        make_m2m=False,
        project_status=project_status,
        situational_status=situational_status,
        status_since=timestamp - datetime.timedelta(days=1),
        monday=datetime.time(10, 0),
    )
    group.teachers.add(*teachers)
    group.students.add(*students)
    return group


@pytest.mark.django_db
def test_group_create_sets_teacher_group_offered_only(timestamp, availability_slots):
    teacher = baker.make(Teacher, project_status=TeacherProjectStatus.NO_GROUP_YET, situational_status="")
    student = baker.make(Student, project_status=StudentProjectStatus.NO_GROUP_YET, situational_status="")
    group = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.PENDING,
    )

    GroupCreateProcessor(group).process()

    teacher.refresh_from_db()
    student.refresh_from_db()
    assert teacher.situational_status == TeacherSituationalStatus.GROUP_OFFERED
    assert student.situational_status == ""


@pytest.mark.django_db
def test_group_confirm_ready_to_start_sets_awaiting_start(timestamp, availability_slots):
    teacher = baker.make(Teacher, project_status=TeacherProjectStatus.NO_GROUP_YET, situational_status="")
    student = baker.make(Student, project_status=StudentProjectStatus.NO_GROUP_YET, situational_status="")
    group = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.PENDING,
    )

    GroupConfirmReadyToStartProcessor(group).process()

    teacher.refresh_from_db()
    student.refresh_from_db()
    group.refresh_from_db()
    assert group.project_status == GroupProjectStatus.AWAITING_START
    assert teacher.situational_status == TeacherSituationalStatus.AWAITING_START
    assert student.situational_status == StudentSituationalStatus.AWAITING_START


@pytest.mark.django_db
def test_group_holiday_sets_holiday_status(timestamp, availability_slots):
    teacher = baker.make(Teacher, project_status=TeacherProjectStatus.NO_GROUP_YET, situational_status="")
    student = baker.make(Student, project_status=StudentProjectStatus.NO_GROUP_YET, situational_status="")
    group = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.WORKING,
        situational_status=GroupSituationalStatus.HOLIDAY,
    )

    StatusSetter.update_related_statuses_for_group(group, timestamp)

    teacher.refresh_from_db()
    student.refresh_from_db()
    assert teacher.situational_status == TeacherSituationalStatus.HOLIDAY
    assert student.situational_status == StudentSituationalStatus.HOLIDAY


@pytest.mark.django_db
def test_group_holiday_respects_high_priority_status(timestamp, availability_slots):
    teacher = baker.make(
        Teacher,
        project_status=TeacherProjectStatus.NO_GROUP_YET,
        situational_status=TeacherSituationalStatus.NEEDS_SUBSTITUTION,
    )
    student = baker.make(
        Student,
        project_status=StudentProjectStatus.NO_GROUP_YET,
        situational_status=StudentSituationalStatus.NO_RESPONSE,
    )
    group = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.WORKING,
        situational_status=GroupSituationalStatus.HOLIDAY,
    )

    StatusSetter.update_related_statuses_for_group(group, timestamp)

    teacher.refresh_from_db()
    student.refresh_from_db()
    assert teacher.situational_status == TeacherSituationalStatus.NEEDS_SUBSTITUTION
    assert student.situational_status == StudentSituationalStatus.NO_RESPONSE


@pytest.mark.django_db
def test_group_abort_keeps_students_with_other_groups_studying(timestamp, availability_slots):
    student = baker.make(Student, project_status=StudentProjectStatus.STUDYING, situational_status="")
    teacher = baker.make(Teacher, project_status=TeacherProjectStatus.WORKING, situational_status="")

    group_one = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.WORKING,
    )
    group_two = _make_group(
        availability_slots=availability_slots,
        timestamp=timestamp,
        teachers=[teacher],
        students=[student],
        project_status=GroupProjectStatus.WORKING,
    )

    GroupAbortProcessor(group_one).process()

    student.refresh_from_db()
    group_two.refresh_from_db()
    assert student.project_status == StudentProjectStatus.STUDYING
    assert group_two.project_status == GroupProjectStatus.WORKING
