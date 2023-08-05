import datetime

import pytest
from model_bakery import baker

from api.models import Group
from api.models.choices.status import (
    CoordinatorProjectStatus,
    GroupProjectStatus,
    StudentProjectStatus,
    TeacherProjectStatus,
)


@pytest.fixture
def group(timestamp, availability_slots):
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        availability_slots_for_auto_matching=availability_slots,
    )

    group.project_status = GroupProjectStatus.PENDING
    # to make sure `status_since` really gets updated:
    group.status_since = timestamp - datetime.timedelta(days=1, hours=1, minutes=10)
    group.coordinators.update(status=CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD)
    group.students.update(status=StudentProjectStatus.NOT_STUDYING)
    group.teachers.update(status=TeacherProjectStatus.AWAITING_OFFER)
    group.save()
    yield group


@pytest.fixture
def active_group(timestamp, availability_slots):
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        availability_slots_for_auto_matching=availability_slots,
    )

    group.project_status = GroupProjectStatus.WORKING
    # to make sure `status_since` really gets updated:
    group.status_since = timestamp - datetime.timedelta(days=1, hours=1, minutes=10)
    group.coordinators.update(status=CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD)
    group.students.update(status=StudentProjectStatus.STUDYING)
    group.teachers.update(status=TeacherProjectStatus.TEACHING_ACCEPTING_MORE)
    group.teachers_former.clear()
    group.students_former.clear()
    group.coordinators_former.clear()
    group.save()
    yield group
