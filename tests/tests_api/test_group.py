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
from api.models.choices.status import (
    CoordinatorProjectStatus,
    GroupProjectStatus,
    StudentProjectStatus,
    TeacherProjectStatus,
)
from api.serializers import GroupWriteSerializer


def test_dashboard_group_list(api_client, availability_slots):
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        availability_slots_for_auto_matching=availability_slots,
    )
    response = api_client.get("/api/dashboard/groups/")

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
                "id": group.language_and_level.pk,
                "language": group.language_and_level.language.name,
                "level": group.language_and_level.level.id,
            },
            "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
            "status": group.project_status,
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


def test_dashboard_group_retrieve(api_client, availability_slots):
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        availability_slots_for_auto_matching=availability_slots,
    )
    response = api_client.get(f"/api/dashboard/groups/{group.pk}/")

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
            "id": group.language_and_level.pk,
            "language": group.language_and_level.language.name,
            "level": group.language_and_level.level.id,
        },
        "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
        "status": group.project_status,
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
    """Compares the given datetime object with timestamp from conftest.py.

    Allows for a one-minute margin between timestamp and the datetime being checked.

    Used e.g. to compare `status_since` attribute after status change.

    For this test to be informative, make sure you manually set status_since to
    some date in the past so that the match with timestamp after status change is not accidental.
    """
    assert date_time - timestamp < datetime.timedelta(minutes=1)


class TestDashboardGroupStart:
    def test_dashboard_group_start_general_check(self, api_client, group, timestamp):
        response = api_client.post(self._make_url(group))

        assert response.status_code == status.HTTP_201_CREATED

        group.refresh_from_db()
        assert group.project_status == GroupProjectStatus.WORKING

        common_status_since = group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        for coordinator in group.coordinators.iterator():
            assert coordinator.project_status in (
                CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD,
                CoordinatorProjectStatus.WORKING_OK,
                CoordinatorProjectStatus.WORKING_LIMIT_REACHED,
            )
            assert coordinator.status_since == common_status_since

            log_event: CoordinatorLogEvent = CoordinatorLogEvent.objects.get(
                coordinator_id=coordinator.pk
            )
            assert log_event.type == CoordinatorLogEventType.TOOK_NEW_GROUP
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for student in group.students.iterator():
            assert student.project_status == StudentProjectStatus.STUDYING
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.STUDY_START
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.project_status in (
                TeacherProjectStatus.TEACHING_ACCEPTING_MORE,
                TeacherProjectStatus.TEACHING_NOT_ACCEPTING_MORE,
            )
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.STUDY_START
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "number_of_groups_to_start, expected_status",
        [
            (CoordinatorGroupLimit.MIN - 1, CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD),
            (CoordinatorGroupLimit.MIN, CoordinatorProjectStatus.WORKING_OK),
            (CoordinatorGroupLimit.MIN + 1, CoordinatorProjectStatus.WORKING_OK),
            (CoordinatorGroupLimit.MAX - 1, CoordinatorProjectStatus.WORKING_OK),
            (CoordinatorGroupLimit.MAX, CoordinatorProjectStatus.WORKING_LIMIT_REACHED),
            (CoordinatorGroupLimit.MAX + 1, CoordinatorProjectStatus.WORKING_LIMIT_REACHED),
        ],
    )
    def test_dashboard_group_start_coordinator_status(  # noqa: PLR0913
        self,
        api_client,
        timestamp,
        number_of_groups_to_start,
        expected_status,
        availability_slots,
    ):
        coordinator = baker.make(Coordinator, _fill_optional=True)
        coordinator.status = CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD
        coordinator.save()

        for _ in range(number_of_groups_to_start):
            group = baker.make(
                Group, _fill_optional=True, availability_slots_for_auto_matching=availability_slots
            )
            group.project_status = GroupProjectStatus.AWAITING_START
            group.coordinators.add(coordinator)
            group.save()

            response = api_client.post(self._make_url(group))
            assert response.status_code == status.HTTP_201_CREATED

        coordinator.refresh_from_db()
        assert coordinator.groups.count() == number_of_groups_to_start
        assert coordinator.status == expected_status
        compare_date_time_with_timestamp(coordinator.status_since, timestamp)

    def test_dashboard_group_start_student_status(self, api_client, timestamp, availability_slots):
        student = baker.make(Student, _fill_optional=True, availability_slots=availability_slots)
        student.status = StudentProjectStatus.AWAITING_START
        student.save()

        group = baker.make(
            Group, _fill_optional=True, availability_slots_for_auto_matching=availability_slots
        )
        group.project_status = GroupProjectStatus.AWAITING_START

        group.students.add(student)

        group.save()

        response = api_client.post(self._make_url(group))
        assert response.status_code == status.HTTP_201_CREATED

        student.refresh_from_db()
        assert student.groups.count() == 1
        assert student.status == StudentProjectStatus.STUDYING
        compare_date_time_with_timestamp(student.status_since, timestamp)

    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-start", kwargs={"pk": group.id})

    @pytest.mark.parametrize(
        "delta, expected_status",
        [
            (-1, TeacherProjectStatus.TEACHING_ACCEPTING_MORE),
            (0, TeacherProjectStatus.TEACHING_NOT_ACCEPTING_MORE),
            (1, TeacherProjectStatus.TEACHING_NOT_ACCEPTING_MORE),
        ],
    )
    def test_dashboard_group_start_teacher_status(  # noqa: PLR0913
        self, api_client, timestamp, delta, expected_status, availability_slots
    ):
        teacher = baker.make(Teacher, _fill_optional=True, availability_slots=availability_slots)
        teacher.simultaneous_groups = 3  # no significance, just more than 1
        teacher.status = TeacherProjectStatus.AWAITING_START
        teacher.save()

        for _ in range(teacher.simultaneous_groups + delta):
            group = baker.make(
                Group, _fill_optional=True, availability_slots_for_auto_matching=availability_slots
            )
            group.project_status = GroupProjectStatus.AWAITING_START
            group.teachers.add(teacher)
            group.save()

            response = api_client.post(self._make_url(group))
            assert response.status_code == status.HTTP_201_CREATED

        teacher.refresh_from_db()
        assert teacher.groups.count() == teacher.simultaneous_groups + delta
        assert teacher.status == expected_status
        compare_date_time_with_timestamp(teacher.status_since, timestamp)


class TestDashboardGroupAbort:
    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-abort", kwargs={"pk": group.id})

    def test_dashboard_group_abort_general_check(self, api_client, active_group, timestamp):
        prev_student_count, prev_teacher_count, prev_coordinator_count = (
            active_group.students.count(),
            active_group.teachers.count(),
            active_group.coordinators.count(),
        )
        response = api_client.post(self._make_url(active_group))
        assert response.status_code == status.HTTP_200_OK

        active_group.refresh_from_db()
        assert active_group.project_status == GroupProjectStatus.ABORTED
        assert active_group.students_former.count() == prev_student_count
        assert active_group.teachers_former.count() == prev_teacher_count
        assert active_group.coordinators_former.count() == prev_coordinator_count

        common_status_since = active_group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        assert not active_group.students.count()
        assert not active_group.teachers.count()
        assert not active_group.coordinators.count()

        for coordinator in active_group.coordinators_former.iterator():
            assert coordinator.project_status in (
                CoordinatorProjectStatus.WORKING_BELOW_THRESHOLD,
                CoordinatorProjectStatus.WORKING_OK,
                CoordinatorProjectStatus.WORKING_LIMIT_REACHED,
            )
            assert coordinator.status_since == common_status_since

            log_event: CoordinatorLogEvent = CoordinatorLogEvent.objects.get(
                coordinator_id=coordinator.pk
            )
            assert log_event.type == CoordinatorLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for student in active_group.students_former.iterator():
            assert student.project_status == StudentProjectStatus.NOT_STUDYING
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in active_group.teachers_former.iterator():
            assert teacher.project_status in (
                TeacherProjectStatus.TEACHING_ACCEPTING_MORE,
                TeacherProjectStatus.TEACHING_NOT_ACCEPTING_MORE,
                TeacherProjectStatus.AWAITING_OFFER,
            )
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.GROUP_ABORTED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_abort_appends_former_entity_lists(self, api_client, active_group, availability_slots):
        # test that lists are not overwritten
        student = baker.make(Student, _fill_optional=True, availability_slots=availability_slots)
        teacher = baker.make(Teacher, _fill_optional=True, availability_slots=availability_slots)
        coordinator = baker.make(Coordinator, _fill_optional=True)
        active_group.students_former.add(student)
        active_group.teachers_former.add(teacher)
        active_group.coordinators_former.add(coordinator)
        active_group.save()

        response = api_client.post(self._make_url(active_group))

        assert response.status_code == status.HTTP_200_OK

        active_group.refresh_from_db()
        assert active_group.project_status == GroupProjectStatus.ABORTED
        assert active_group.students_former.filter(pk=student.pk).exists()
        assert active_group.teachers_former.filter(pk=teacher.pk).exists()
        assert active_group.coordinators_former.filter(pk=coordinator.pk).exists()


class TestGroupCreation:
    def get_data(self, group: Group):
        return {
            "lesson_duration_in_minutes": 30,
            "communication_language_mode": group.communication_language_mode,
            "availability_slots_for_auto_matching": [
                a.id for a in group.availability_slots_for_auto_matching.iterator()
            ],
            "language_and_level": group.language_and_level.id,
            "monday": "10:00:00",
            "coordinators": [c.pk for c in group.coordinators.iterator()],
            "students": [s.pk for s in group.students.iterator()],
            "teachers": [t.pk for t in group.teachers.iterator()],
        }

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/dashboard/groups/",
            "/api/groups/",
        ],
    )
    def test_group_create_general(self, api_client, group: Group, timestamp, endpoint: str):
        data_to_create = self.get_data(group)
        response = api_client.post(endpoint, data_to_create)
        assert response.status_code == status.HTTP_201_CREATED
        created_group = Group.objects.get(id=response.data["id"])
        created_group_serializer = GroupWriteSerializer(created_group)
        for field, val in data_to_create.items():
            assert val == response.data[field]
            assert val == created_group_serializer.data[field]

        assert group.project_status == GroupProjectStatus.PENDING

        common_status_since = created_group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        for student in group.students.iterator():
            assert student.status == StudentProjectStatus.GROUP_OFFERED
            assert student.status_since == common_status_since
            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.GROUP_OFFERED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.status == TeacherProjectStatus.GROUP_OFFERED
            assert teacher.status_since == common_status_since
            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.GROUP_OFFERED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)


class TestDashboardGroupConfirmReadyToStart:
    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-confirm-ready-to-start", kwargs={"pk": group.id})

    def test_dashboard_group_confirm_ready_to_start_general_check(
        self, api_client, group, timestamp
    ):
        response = api_client.post(self._make_url(group))

        assert response.status_code == status.HTTP_200_OK

        group.refresh_from_db()
        assert group.project_status == GroupProjectStatus.AWAITING_START
        common_status_since = group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        for coordinator in group.coordinators.iterator():
            log_event: CoordinatorLogEvent = CoordinatorLogEvent.objects.get(
                coordinator_id=coordinator.pk
            )
            assert log_event.type == CoordinatorLogEventType.TOOK_NEW_GROUP

        for student in group.students.iterator():
            assert student.project_status == StudentProjectStatus.AWAITING_START
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.GROUP_CONFIRMED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.project_status == TeacherProjectStatus.AWAITING_START
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.GROUP_CONFIRMED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)


# TODO add tests for internal router
