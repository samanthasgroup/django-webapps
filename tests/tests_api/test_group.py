import datetime

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from api.models import (
    Coordinator,
    CoordinatorLogEvent,
    Group,
    Student,
    StudentLogEvent,
    Teacher,
    TeacherLogEvent,
)
from api.models.auxil.constants import CoordinatorGroupLimit
from api.models.choices.log_event_type import (
    CoordinatorLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.status import CoordinatorStatus, GroupStatus, StudentStatus, TeacherStatus


def test_public_group_list(api_client):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    response = api_client.get("/api/public/groups/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json == [
        {
            "id": group.pk,
            "communication_language_mode": group.communication_language_mode,
            "monday": str(group.monday),
            "tuesday": str(group.tuesday),
            "wednesday": str(group.wednesday),
            "thursday": str(group.thursday),
            "friday": str(group.friday),
            "saturday": str(group.saturday),
            "sunday": str(group.sunday),
            "language_and_level": {
                "language": group.language_and_level.language.name,
                "level": group.language_and_level.level.id,
            },
            "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
            "status": group.status,
            "start_date": group.start_date.isoformat(),
            "end_date": group.end_date.isoformat(),
            "telegram_chat_url": group.telegram_chat_url,
            "coordinators": [
                {
                    "id": coordinator.pk,
                    "full_name": coordinator.personal_info.full_name,
                }
                for coordinator in group.coordinators.all()
            ],
            "teachers": [
                {
                    "id": teacher.pk,
                    "full_name": teacher.personal_info.full_name,
                }
                for teacher in group.teachers.all()
            ],
            "students_count": group.students.count(),
            "is_for_staff_only": group.is_for_staff_only,
        }
    ]


def test_public_group_retrieve(api_client):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    response = api_client.get(f"/api/public/groups/{group.pk}/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json == {
        "id": group.pk,
        "communication_language_mode": group.communication_language_mode,
        "monday": str(group.monday),
        "tuesday": str(group.tuesday),
        "wednesday": str(group.wednesday),
        "thursday": str(group.thursday),
        "friday": str(group.friday),
        "saturday": str(group.saturday),
        "sunday": str(group.sunday),
        "language_and_level": {
            "language": group.language_and_level.language.name,
            "level": group.language_and_level.level.id,
        },
        "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
        "status": group.status,
        "start_date": group.start_date.isoformat(),
        "end_date": group.end_date.isoformat(),
        "telegram_chat_url": group.telegram_chat_url,
        "coordinators": [
            {
                "id": coordinator.pk,
                "full_name": coordinator.personal_info.full_name,
            }
            for coordinator in group.coordinators.all()
        ],
        "teachers": [
            {
                "id": teacher.pk,
                "full_name": teacher.personal_info.full_name,
            }
            for teacher in group.teachers.all()
        ],
        "students": [
            {
                "id": student.pk,
                "full_name": student.personal_info.full_name,
            }
            for student in group.students.all()
        ],
        "is_for_staff_only": group.is_for_staff_only,
    }


def compare_date_time_with_timestamp(date_time: datetime.datetime, timestamp: datetime.datetime):
    assert date_time.year == timestamp.year
    assert date_time.month == timestamp.month
    assert date_time.day == timestamp.day
    assert date_time.hour == timestamp.hour
    assert date_time.minute == timestamp.minute


@pytest.fixture
def group(timestamp):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)

    group.status = GroupStatus.PENDING
    # to make sure `status_since` really gets updated:
    group.status_since = timestamp - datetime.timedelta(days=1, hours=1, minutes=10)
    group.coordinators.update(status=CoordinatorStatus.WORKING_BELOW_THRESHOLD)
    group.students.update(status=StudentStatus.AWAITING_OFFER)
    group.teachers.update(status=TeacherStatus.AWAITING_OFFER)
    group.save()
    yield group


@pytest.fixture
def active_group(timestamp):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)

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


class TestPublicGroupStart:
    def test_public_group_start_general_check(self, api_client, group, timestamp):
        response = api_client.post(self._make_url(group))

        assert response.status_code == status.HTTP_201_CREATED

        group.refresh_from_db()
        assert group.status == GroupStatus.WORKING

        common_status_since = group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        for coordinator in group.coordinators.iterator():
            assert coordinator.status in (
                CoordinatorStatus.WORKING_BELOW_THRESHOLD,
                CoordinatorStatus.WORKING_OK,
                CoordinatorStatus.WORKING_LIMIT_REACHED,
            )
            assert coordinator.status_since == common_status_since

            log_event: CoordinatorLogEvent = CoordinatorLogEvent.objects.get(
                coordinator_id=coordinator.pk
            )
            assert log_event.type == CoordinatorLogEventType.TOOK_NEW_GROUP
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for student in group.students.iterator():
            assert student.status == StudentStatus.STUDYING
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.STUDY_START
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.status in (
                TeacherStatus.TEACHING_ACCEPTING_MORE,
                TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            )
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.STUDY_START
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "number_of_groups_to_start, expected_status",
        [
            (CoordinatorGroupLimit.MIN - 1, CoordinatorStatus.WORKING_BELOW_THRESHOLD),
            (CoordinatorGroupLimit.MIN, CoordinatorStatus.WORKING_OK),
            (CoordinatorGroupLimit.MIN + 1, CoordinatorStatus.WORKING_OK),
            (CoordinatorGroupLimit.MAX - 1, CoordinatorStatus.WORKING_OK),
            (CoordinatorGroupLimit.MAX, CoordinatorStatus.WORKING_LIMIT_REACHED),
            (CoordinatorGroupLimit.MAX + 1, CoordinatorStatus.WORKING_LIMIT_REACHED),
        ],
    )
    def test_public_group_start_coordinator_status(
        self, api_client, timestamp, number_of_groups_to_start, expected_status
    ):
        coordinator = baker.make(Coordinator, _fill_optional=True)
        coordinator.status = CoordinatorStatus.WORKING_BELOW_THRESHOLD
        coordinator.save()

        for _ in range(number_of_groups_to_start):
            group = baker.make(Group, _fill_optional=True)
            group.status = GroupStatus.AWAITING_START
            group.coordinators.add(coordinator)
            group.save()

            response = api_client.post(self._make_url(group))
            assert response.status_code == status.HTTP_201_CREATED

        coordinator.refresh_from_db()
        assert coordinator.groups.count() == number_of_groups_to_start
        assert coordinator.status == expected_status
        compare_date_time_with_timestamp(coordinator.status_since, timestamp)

    def test_public_group_start_student_status(self, api_client, timestamp):
        student = baker.make(Student, _fill_optional=True)
        student.status = StudentStatus.AWAITING_START
        student.save()

        group = baker.make(Group, _fill_optional=True)
        group.status = GroupStatus.AWAITING_START

        group.students.add(student)

        group.save()

        response = api_client.post(self._make_url(group))
        assert response.status_code == status.HTTP_201_CREATED

        student.refresh_from_db()
        assert student.groups.count() == 1
        assert student.status == StudentStatus.STUDYING
        compare_date_time_with_timestamp(student.status_since, timestamp)

    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-start", kwargs={"pk": group.id})

    @pytest.mark.parametrize(
        "delta, expected_status",
        [
            (-1, TeacherStatus.TEACHING_ACCEPTING_MORE),
            (0, TeacherStatus.TEACHING_NOT_ACCEPTING_MORE),
            (1, TeacherStatus.TEACHING_NOT_ACCEPTING_MORE),
        ],
    )
    def test_public_group_start_teacher_status(
        self, api_client, timestamp, delta, expected_status
    ):
        teacher = baker.make(Teacher, _fill_optional=True)
        teacher.simultaneous_groups = 3  # no significance, just more than 1
        teacher.status = TeacherStatus.AWAITING_START
        teacher.save()

        for _ in range(teacher.simultaneous_groups + delta):
            group = baker.make(Group, _fill_optional=True)
            group.status = GroupStatus.AWAITING_START
            group.teachers.add(teacher)
            group.save()

            response = api_client.post(self._make_url(group))
            assert response.status_code == status.HTTP_201_CREATED

        teacher.refresh_from_db()
        assert teacher.groups.count() == teacher.simultaneous_groups + delta
        assert teacher.status == expected_status
        compare_date_time_with_timestamp(teacher.status_since, timestamp)


class TestPublicGroupAbort:
    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-abort", kwargs={"pk": group.id})

    def test_public_group_abort_general_check(self, api_client, active_group, timestamp):
        response = api_client.post(self._make_url(active_group))

        assert response.status_code == status.HTTP_200_OK

        active_group.refresh_from_db()
        assert active_group.status == GroupStatus.ABORTED

        common_status_since = active_group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        assert not active_group.students.count()
        assert not active_group.teachers.count()
        assert not active_group.coordinators.count()

        for coordinator in active_group.coordinators_former.iterator():
            assert coordinator.status in (
                CoordinatorStatus.WORKING_BELOW_THRESHOLD,
                CoordinatorStatus.WORKING_OK,
                CoordinatorStatus.WORKING_LIMIT_REACHED,
            )
            assert coordinator.status_since == common_status_since

            log_event: CoordinatorLogEvent = CoordinatorLogEvent.objects.get(
                coordinator_id=coordinator.pk
            )
            assert log_event.type == CoordinatorLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for student in active_group.students_former.iterator():
            assert student.status == StudentStatus.AWAITING_OFFER
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in active_group.teachers_former.iterator():
            assert teacher.status in (
                TeacherStatus.TEACHING_ACCEPTING_MORE,
                TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
                TeacherStatus.AWAITING_OFFER,
            )
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_abort_appends_former_entity_lists(self, api_client, active_group):
        # test that lists are not overwritten
        student = baker.make(Student, _fill_optional=True)
        teacher = baker.make(Teacher, _fill_optional=True)
        coordinator = baker.make(Coordinator, _fill_optional=True)
        active_group.students_former.add(student)
        active_group.teachers_former.add(teacher)
        active_group.coordinators_former.add(coordinator)
        active_group.save()

        response = api_client.post(self._make_url(active_group))

        assert response.status_code == status.HTTP_200_OK

        active_group.refresh_from_db()
        assert active_group.status == GroupStatus.ABORTED
        assert active_group.students_former.filter(pk=student.pk).exists()
        assert active_group.teachers_former.filter(pk=teacher.pk).exists()
        assert active_group.coordinators_former.filter(pk=coordinator.pk).exists()
