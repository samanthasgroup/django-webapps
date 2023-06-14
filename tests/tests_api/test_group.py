import datetime

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from api.models import CoordinatorLogEvent, Group, LogEvent, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_types import (
    CoordinatorLogEventType,
    StudentLogEventType,
    TeacherLogEventType,
)
from api.models.choices.statuses import (
    CoordinatorStatus,
    GroupStatus,
    StudentStatus,
    TeacherStatus,
)


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


class TestPublicGroupStart:
    def test_public_group_start_general_check(self, api_client, group, timestamp):
        response = api_client.post(self._make_url(group))

        assert response.status_code == status.HTTP_201_CREATED

        group.refresh_from_db()
        assert group.status == GroupStatus.WORKING

        common_status_since = group.status_since
        assert common_status_since.day == timestamp.day
        assert common_status_since.hour == timestamp.hour
        assert common_status_since.minute == timestamp.minute

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
            self._compare_log_event_date_time_with_timestamp(log_event, timestamp)

        for student in group.students.iterator():
            assert student.status == StudentStatus.STUDYING
            assert student.status_since == common_status_since

            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.STUDY_START
            self._compare_log_event_date_time_with_timestamp(log_event, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.status in (
                TeacherStatus.TEACHING_ACCEPTING_MORE,
                TeacherStatus.TEACHING_NOT_ACCEPTING_MORE,
            )
            assert teacher.status_since == common_status_since

            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.STUDY_START
            self._compare_log_event_date_time_with_timestamp(log_event, timestamp)

    @staticmethod
    def _compare_log_event_date_time_with_timestamp(
        log_event: LogEvent, timestamp: datetime.datetime
    ):
        """Unlike statuses, log events get their own automatic timestamps,
        so exact equality cannot be checked.
        """
        assert log_event.date_time.year == timestamp.year
        assert log_event.date_time.month == timestamp.month
        assert log_event.date_time.day == timestamp.day
        assert log_event.date_time.hour == timestamp.hour
        assert log_event.date_time.minute == timestamp.minute

    @staticmethod
    def _make_url(group: Group) -> str:
        return reverse("groups-start", kwargs={"pk": group.id})
