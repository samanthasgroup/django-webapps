import copy

import pytest
from django.utils import timezone
from model_bakery import baker

from api.models import AgeRange, LanguageAndLevel, Student, Teacher
from api.models.choices.communication_language_mode import CommunicationLanguageMode
from api.processors.services.group_builder import MAX_WAITING_TIME, GroupBuilder, GroupCandidate


@pytest.fixture
def group_candidate():
    teacher = baker.make(Teacher, _fill_optional=True, make_m2m=True)
    age_range = AgeRange.objects.first()
    students = baker.make(Student, _fill_optional=True, make_m2m=True, _quantity=5)
    return GroupCandidate(
        language_and_level=LanguageAndLevel.objects.filter(level_id="B1", language_id="en").first(),
        communication_language_mode=CommunicationLanguageMode(teacher.personal_info.communication_language_mode),
        age_range=age_range,
        teacher=teacher,
        students=students,
        day_time_slots=[],
    )


def test_compare_priority_with_same_level(group_candidate):
    other_group_candidate = group_candidate
    assert GroupBuilder._compare_groups_priority(group_candidate, other_group_candidate) == 0


def test_compare_priority_with_lower_level(group_candidate):
    other_group_candidate = copy.copy(group_candidate)
    other_group_candidate.language_and_level = LanguageAndLevel.objects.filter(level_id="A1", language_id="en").first()
    assert GroupBuilder._compare_groups_priority(group_candidate, other_group_candidate) == 1


def test_compare_priority_with_higher_level(group_candidate):
    other_group_candidate = copy.copy(group_candidate)
    other_group_candidate.language_and_level = LanguageAndLevel.objects.filter(
        level__id="C1", language__id="en"
    ).first()
    assert GroupBuilder._compare_groups_priority(group_candidate, other_group_candidate) == -1


def test_compare_priority_with_more_waiting_students(group_candidate):
    other_group_candidate = copy.copy(group_candidate)
    waiting_students = baker.make(
        Student,
        _fill_optional=True,
        make_m2m=True,
        _quantity=5,
        status_since=timezone.now() - MAX_WAITING_TIME,
    )
    fresh_students = baker.make(Student, _fill_optional=True, make_m2m=True, _quantity=5)
    other_group_candidate.students = waiting_students
    group_candidate.students = fresh_students
    assert GroupBuilder._compare_groups_priority(group_candidate, other_group_candidate) == -1


# TODO: add more tests on building functionality
