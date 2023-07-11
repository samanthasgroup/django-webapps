import datetime

import pytest
from model_bakery import baker

from api.models import Group
from api.models.choices.status import CoordinatorStatus, GroupStatus, StudentStatus, TeacherStatus


@pytest.fixture
def group(timestamp, availability_slots):
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        availability_slots_for_auto_matching=availability_slots,
    )

    group.status = GroupStatus.PENDING
    # to make sure `status_since` really gets updated:
    group.status_since = timestamp - datetime.timedelta(days=1, hours=1, minutes=10)
    group.coordinators.update(status=CoordinatorStatus.WORKING_BELOW_THRESHOLD)
    group.students.update(status=StudentStatus.AWAITING_OFFER)
    group.teachers.update(status=TeacherStatus.AWAITING_OFFER)
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

    group.status = GroupStatus.WORKING
    # to make sure `status_since` really gets updated:
    group.status_since = timestamp - datetime.timedelta(days=1, hours=1, minutes=10)
    group.coordinators.update(status=CoordinatorStatus.WORKING_BELOW_THRESHOLD)
    group.students.update(status=StudentStatus.STUDYING)
    group.teachers.update(status=TeacherStatus.TEACHING_ACCEPTING_MORE)
    group.teachers_former.clear()
    group.students_former.clear()
    group.coordinators_former.clear()
    group.save()
    yield group
