import datetime

import pytest
import pytz
from model_bakery import baker, seq
from rest_framework import status

from api.models import (
    AgeRange,
    Coordinator,
    DayAndTimeSlot,
    LanguageAndLevel,
    NonTeachingHelp,
    PersonalInfo,
    Student,
)
from api.models.choices.log_event_type import CoordinatorLogEventType, StudentLogEventType
from api.models.choices.status import StudentProjectStatus, StudentSituationalStatus
from api.models.group import Group
from api.models.log_event import CoordinatorLogEvent, StudentLogEvent
from api.serializers import DashboardStudentSerializer, StudentWriteSerializer
from tests.tests_api.asserts import (
    assert_date_time_with_timestamp,
    assert_response_data,
    assert_response_data_list,
)


def test_student_create(api_client, faker):
    initial_count = Student.objects.count()
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
    age_range_id = AgeRange.objects.first().id
    teaching_languages_and_levels_ids = [
        LanguageAndLevel.objects.first().id,
        LanguageAndLevel.objects.last().id,
    ]
    availability_slots_ids = [
        DayAndTimeSlot.objects.first().id,
        DayAndTimeSlot.objects.last().id,
    ]
    non_teaching_help_ids = [
        NonTeachingHelp.objects.first().id,
        NonTeachingHelp.objects.last().id,
    ]
    data = {
        "personal_info": personal_info.id,
        "comment": faker.text(),
        "project_status": StudentProjectStatus.NO_GROUP_YET.value,
        "situational_status": "",
        "status_since": faker.date_time(tzinfo=pytz.utc),
        "age_range": age_range_id,
        "teaching_languages_and_levels": teaching_languages_and_levels_ids,
        "is_member_of_speaking_club": faker.pybool(),
        "can_read_in_english": faker.pybool(),
        "non_teaching_help_required": non_teaching_help_ids,
        "availability_slots": availability_slots_ids,
    }
    response = api_client.post("/api/students/", data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Student.objects.count() == initial_count + 1

    m2m_fields = [
        "teaching_languages_and_levels",
        "availability_slots",
        "non_teaching_help_required",
    ]  # TODO children
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert Student.objects.filter(**data).exists()


def test_student_retrieve(api_client, availability_slots):
    student = baker.make(Student, make_m2m=True, availability_slots=availability_slots)
    response = api_client.get(f"/api/students/{student.personal_info.id}/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    languages_and_levels = [
        {
            "id": language_and_level.id,
            "language": {
                "id": language_and_level.language.id,
                "name": language_and_level.language.name,
            },
            "level": language_and_level.level.id,
        }
        for language_and_level in student.teaching_languages_and_levels.all()
    ]
    availability_slots = [
        {
            "id": slot.id,
            "time_slot": {
                "id": slot.time_slot.id,
                "from_utc_hour": str(slot.time_slot.from_utc_hour),
                "to_utc_hour": str(slot.time_slot.to_utc_hour),
            },
            "day_of_week_index": slot.day_of_week_index,
        }
        for slot in student.availability_slots.all()
    ]
    assert response_json == {
        "personal_info": student.personal_info.id,
        "age_range": {
            "id": student.age_range.id,
            "age_from": student.age_range.age_from,
            "age_to": student.age_range.age_to,
            "type": student.age_range.type,
        },
        "teaching_languages_and_levels": languages_and_levels,
        "availability_slots": availability_slots,
        "comment": student.comment,
        "project_status": student.project_status,
        "situational_status": student.situational_status,
        "status_since": student.status_since.isoformat().replace("+00:00", "Z"),
        "is_member_of_speaking_club": student.is_member_of_speaking_club,
        "can_read_in_english": student.can_read_in_english,
        # These are optional, so baker won't generate them (unless _fill_optional is True)
        "non_teaching_help_required": [],
        "smalltalk_test_result": None,
    }


def test_student_update(api_client, availability_slots):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    Student.objects.get(pk=student.pk)
    fields_to_update = {
        "project_status": StudentProjectStatus.BANNED,
        "is_member_of_speaking_club": True,
        "availability_slots": [i.id for i in availability_slots[2:5]],
    }

    response = api_client.patch(
        f"/api/students/{student.personal_info.id}/", data=fields_to_update
    )
    new_student_data = StudentWriteSerializer(student).data
    for field, val in fields_to_update.items():
        new_student_data[field] = val
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, new_student_data)

    db_student = Student.objects.get(pk=student.pk)
    db_studnet_data = StudentWriteSerializer(db_student).data
    assert_response_data(db_studnet_data, new_student_data)


def test_dashboard_student_retrieve(api_client, faker, availability_slots):
    utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
    sign = "+" if utc_offset_hours >= 0 else "-"
    utc_offset_minutes = faker.random_element([0, 30])
    utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
    student = baker.make(
        Student,
        make_m2m=True,
        personal_info__utc_timedelta=utc_timedelta,
        availability_slots=availability_slots,
    )
    response = api_client.get(f"/api/dashboard/students/{student.personal_info.id}/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    languages_and_levels = [
        {
            "id": language_and_level.pk,
            "language": language_and_level.language.name,
            "level": language_and_level.level.id,
        }
        for language_and_level in student.teaching_languages_and_levels.all()
    ]
    availability_slots = [
        {
            "id": slot.pk,
            "day_of_week_index": slot.day_of_week_index,
            "from_utc_hour": slot.time_slot.from_utc_hour.isoformat(),
            "to_utc_hour": slot.time_slot.to_utc_hour.isoformat(),
        }
        for slot in student.availability_slots.all()
    ]
    assert response_json == {
        "id": student.personal_info.id,
        "first_name": student.personal_info.first_name,
        "last_name": student.personal_info.last_name,
        "age_range": f"{student.age_range.age_from}-{student.age_range.age_to}",
        "teaching_languages_and_levels": languages_and_levels,
        "availability_slots": availability_slots,
        "comment": student.comment,
        "project_status": student.project_status,
        "situational_status": student.situational_status,
        "communication_language_mode": student.personal_info.communication_language_mode,
        "is_member_of_speaking_club": student.is_member_of_speaking_club,
        "utc_timedelta": f"UTC{sign}{utc_offset_hours:02}:{utc_offset_minutes:02}",
        "non_teaching_help_required": {
            "career_strategy": False,
            "career_switch": False,
            "cv_proofread": False,
            "cv_write_edit": False,
            "job_search": False,
            "linkedin": False,
            "mock_interview": False,
            "portfolio": False,
            "translate_docs": False,
            "uni_abroad": False,
        },
    }


def test_dashboard_student_list(api_client, faker, availability_slots):
    utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
    sign = "+" if utc_offset_hours >= 0 else "-"
    utc_offset_minutes = faker.random_element([0, 30])
    utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
    student = baker.make(
        Student,
        make_m2m=True,
        personal_info__utc_timedelta=utc_timedelta,
        availability_slots=availability_slots,
    )
    response = api_client.get("/api/dashboard/students/")

    assert response.status_code == status.HTTP_200_OK
    student_data = DashboardStudentSerializer(student).data
    student_data["utc_timedelta"] = f"UTC{sign}{utc_offset_hours:02}:{utc_offset_minutes:02}"
    student_data["non_teaching_help_required"] = {
        "career_strategy": False,
        "career_switch": False,
        "cv_proofread": False,
        "cv_write_edit": False,
        "job_search": False,
        "linkedin": False,
        "mock_interview": False,
        "portfolio": False,
        "translate_docs": False,
        "uni_abroad": False,
    }
    assert_response_data_list(response.data, [student_data])


class TestDashboardStudentTransfer:
    def test_dashboard_student_transfer_general_check(
        self, api_client, active_group: Group, timestamp, availability_slots
    ):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        old_group = baker.make(
            Group,
            _fill_optional=True,
            make_m2m=True,
            availability_slots_for_auto_matching=availability_slots,
        )
        old_group.students.add(student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/transfer/",
            data={"to_group_id": active_group.pk, "from_group_id": old_group.pk},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        current_student_groups = student.groups.all()
        assert len(current_student_groups) == 1
        assert current_student_groups[0] == active_group
        assert student in old_group.students_former.all()
        assert student not in old_group.students.all()
        log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
        assert log_event.type == StudentLogEventType.TRANSFERRED
        assert student.project_status == StudentProjectStatus.STUDYING
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_dashboard_student_transfer_from_empty_group(
        self, api_client, active_group: Group, availability_slots
    ):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        old_group = baker.make(
            Group,
            _fill_optional=True,
            make_m2m=True,
            availability_slots_for_auto_matching=availability_slots,
        )
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/transfer/",
            data={"to_group_id": active_group.pk, "from_group_id": old_group.pk},
        )
        assert response.status_code == status.HTTP_409_CONFLICT


class TestStudentWithPersonalInfo:
    def test_can_filter_by_coordinator_email(self, api_client, faker, availability_slots):
        utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
        utc_offset_minutes = faker.random_element([0, 30])
        utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
        student = baker.make(
            Student,
            make_m2m=True,
            personal_info__utc_timedelta=utc_timedelta,
            availability_slots=availability_slots,
        )

        other_student = baker.make(
            Student,
            make_m2m=True,
            personal_info__utc_timedelta=utc_timedelta,
            availability_slots=availability_slots,
        )  # This student is not in the group and should not be included in the response.
        coordinator = baker.make(Coordinator, make_m2m=True, _fill_optional=True)
        group = baker.make(
            Group,
            _fill_optional=True,
            make_m2m=True,
            availability_slots_for_auto_matching=availability_slots,
        )
        group.students.add(student)
        group.coordinators.add(coordinator)

        response = api_client.get(
            "/api/dashboard/students_with_personal_info/",
            data={"for_coordinator_email": coordinator.personal_info.email},
        )
        assert response.status_code == status.HTTP_200_OK

        returned_ids = [student["id"] for student in response.json()]

        assert student.personal_info.id in returned_ids
        assert other_student.personal_info.id not in returned_ids

    @pytest.mark.parametrize("project_status", StudentProjectStatus.values)
    def test_can_filter_by_project_status(self, api_client, availability_slots, project_status):
        group = baker.make(
            Group,
            make_m2m=True,
            _fill_optional=True,
            availability_slots_for_auto_matching=availability_slots,
        )

        students = [
            baker.make(
                Student,
                make_m2m=True,
                personal_info__utc_timedelta=datetime.timedelta(),
                availability_slots=availability_slots,
                project_status=ps,
            )
            for ps in StudentProjectStatus.values
        ]

        group.students.add(*students)

        response = api_client.get(
            "/api/dashboard/students_with_personal_info/",
            data={"project_status": project_status},
        )

        assert response.status_code == status.HTTP_200_OK

        returned_statuses = [student["project_status"] for student in response.json()]

        assert all(returned_status == project_status for returned_status in returned_statuses)


class TestDashboardStudentMissedClass:
    def _create_logs_for_past_missed_days(
        self, past_missed_days: list[int], timestamp, student
    ) -> None:
        for days in past_missed_days:
            date_time = timestamp - datetime.timedelta(days=days)
            log_event = StudentLogEvent.objects.create(
                student=student,
                type=StudentLogEventType.MISSED_CLASS_SILENTLY,
            )
            log_event.date_time = date_time
            log_event.save()

    def test_dashboard_student_missed_class_general_checks(
        self, api_client, active_group: Group, timestamp, availability_slots
    ):
        student = baker.make(
            Student,
            situational_status="",
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/missed_class/",
            data={"group_id": active_group.pk, "notified": True},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
        assert log_event.type == StudentLogEventType.MISSED_CLASS_NOTIFIED
        assert student.situational_status == ""
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

        self._create_logs_for_past_missed_days([21, 15, 10], timestamp, student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/missed_class/",
            data={"group_id": active_group.pk, "notified": False},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.MISSED_CLASS_SILENTLY
        assert student.situational_status == ""
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "past_missed_days",
        [[2, 10], [3, 10, 12], [0, 0], [13, 13], [12, 13], [1, 2], [26, 21, 4, 9]],
    )
    def test_dashboard_student_missed_class_reached_limit(  # noqa: PLR0913
        self, api_client, active_group: Group, timestamp, availability_slots, past_missed_days
    ):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student)
        self._create_logs_for_past_missed_days(past_missed_days, timestamp, student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/missed_class/",
            data={"group_id": active_group.pk, "notified": False},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.MISSED_CLASS_SILENTLY
        assert student.situational_status == StudentSituationalStatus.NOT_ATTENDING
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "past_missed_days",
        [[0], [3], [21, 14], [14, 14], [14, 15], [100, 35], [10, 15, 20], [25, 24, 14, 20]],
    )
    def test_dashboard_student_missed_class_not_reached_limit(  # noqa: PLR0913
        self, api_client, active_group: Group, timestamp, availability_slots, past_missed_days
    ):
        student = baker.make(
            Student,
            situational_status="",
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student)
        self._create_logs_for_past_missed_days(past_missed_days, timestamp, student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/missed_class/",
            data={"group_id": active_group.pk, "notified": False},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        student.refresh_from_db()
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.MISSED_CLASS_SILENTLY
        assert student.situational_status == ""
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_dashboard_student_missed_class_bad_group(
        self, api_client, active_group: Group, availability_slots
    ):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/missed_class/",
            data={"group_id": active_group.pk, "notified": False},
        )
        assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/dashboard/students/",
        "/api/students/",
    ],
)
def test_dashboard_student_went_on_leave(api_client, availability_slots, timestamp, endpoint):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    response = api_client.post(
        f"{endpoint}{student.personal_info.id}/went_on_leave/",
    )
    student.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
    assert log_event.type == StudentLogEventType.GONE_ON_LEAVE
    assert student.project_status == StudentProjectStatus.ON_LEAVE
    assert_date_time_with_timestamp(log_event.date_time, timestamp)


class TestDashboardStudentReturnedFromLeave:
    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/dashboard/students/",
            "/api/students/",
        ],
    )
    def test_no_group(self, api_client, availability_slots, timestamp, endpoint):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        response = api_client.post(
            f"{endpoint}{student.personal_info.id}/returned_from_leave/",
        )
        student.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: StudentLogEvent | None = StudentLogEvent.objects.filter(
            student_id=student.pk
        ).last()
        assert log_event is not None and log_event.type == StudentLogEventType.RETURNED_FROM_LEAVE
        assert student.project_status == StudentProjectStatus.NO_GROUP_YET
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/dashboard/students/",
            "/api/students/",
        ],
    )
    def test_with_group(  # noqa: PLR0913
        self,
        api_client,
        availability_slots,
        timestamp,
        active_group: Group,
        endpoint,
    ):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student)
        response = api_client.post(
            f"{endpoint}{student.personal_info.id}/returned_from_leave/",
        )
        student.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event is not None and log_event.type == StudentLogEventType.RETURNED_FROM_LEAVE
        assert student.project_status == StudentProjectStatus.STUDYING
        assert_date_time_with_timestamp(log_event.date_time, timestamp)


class TestDashboardStudentListByTimeSlots:
    def test_same_slots(self, api_client, availability_slots):
        slots_to_test = availability_slots[0:2]
        Student.objects.all().delete()
        student1 = baker.make(
            Student,
            project_status=StudentProjectStatus.NO_GROUP_YET,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=slots_to_test,
        )
        student2 = baker.make(
            Student,
            make_m2m=True,
            project_status=StudentProjectStatus.NO_GROUP_YET,
            _fill_optional=True,
            availability_slots=slots_to_test,
        )
        response = api_client.get(
            "/api/dashboard/students/available_students_list/",
            data={"time_slot_ids": [s.pk for s in slots_to_test]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {"full_name": student1.personal_info.full_name, "id": student1.pk},
            {"full_name": student2.personal_info.full_name, "id": student2.pk},
        ]

    def test_different_slots(self, api_client, availability_slots):
        slots_to_test = availability_slots[0:2]
        Student.objects.all().delete()
        baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots[4:5],
        )
        response = api_client.get(
            "/api/dashboard/students/available_students_list/",
            data={"time_slot_ids": [s.pk for s in slots_to_test]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_different_project_status(self, api_client, availability_slots):
        slots_to_test = availability_slots[0:2]
        Student.objects.all().delete()
        baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            project_status=StudentProjectStatus.STUDYING,
            availability_slots=slots_to_test,
        )
        response = api_client.get(
            "/api/dashboard/students/available_students_list/",
            data={"time_slot_ids": [s.pk for s in slots_to_test]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_wrong_input_params(self, api_client, availability_slots):
        slots_to_test = availability_slots[0:2]
        Student.objects.all().delete()
        baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            project_status=StudentProjectStatus.STUDYING,
            availability_slots=slots_to_test,
        )
        response = api_client.get(
            "/api/dashboard/students/available_students_list/",
            data={"time_slot_ids": [availability_slots[0].pk]},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_wrong_time_slots(self, api_client, availability_slots):
        slots_to_test = availability_slots[0:2]
        Student.objects.all().delete()
        baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            project_status=StudentProjectStatus.STUDYING,
            availability_slots=slots_to_test,
        )
        response = api_client.get(
            "/api/dashboard/students/available_students_list/",
            data={"time_slot_ids": [-1, -2]},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_dashboard_student_finished_and_left(
    api_client, availability_slots, active_group, timestamp
):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    response = api_client.post(
        f"/api/dashboard/students/{student.personal_info.id}/finished_and_left/",
    )
    student.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
    assert log_event.type == StudentLogEventType.FINISHED_AND_LEAVING
    assert student.project_status == StudentProjectStatus.FINISHED
    assert_date_time_with_timestamp(log_event.date_time, timestamp)
    student2 = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.students.add(student2)
    response = api_client.post(
        f"/api/dashboard/students/{student2.personal_info.id}/finished_and_left/",
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_dashboard_student_put_on_wait(api_client, availability_slots, active_group, timestamp):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    response = api_client.post(
        f"/api/dashboard/students/{student.personal_info.id}/put_in_waiting_queue/",
    )
    student.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
    assert log_event.type == StudentLogEventType.AWAITING_OFFER
    assert student.project_status == StudentProjectStatus.NO_GROUP_YET
    assert_date_time_with_timestamp(log_event.date_time, timestamp)
    student2 = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.students.add(student2)
    response = api_client.post(
        f"/api/dashboard/students/{student2.personal_info.id}/put_in_waiting_queue/",
    )
    assert response.status_code == status.HTTP_409_CONFLICT


class TestDashboardActiveStudentsWithNoGroups:
    def test_general_check(self, faker, api_client, active_group: Group, availability_slots):
        Student.objects.all().delete()
        utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
        sign = "+" if utc_offset_hours >= 0 else "-"
        utc_offset_minutes = faker.random_element([0, 30])
        utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
        student = baker.make(
            Student,
            project_status=StudentProjectStatus.STUDYING,
            _fill_optional=True,
            availability_slots=availability_slots,
            personal_info__utc_timedelta=utc_timedelta,
        )
        baker.make(
            Student,
            project_status=StudentProjectStatus.NO_GROUP_YET,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        student_with_group = baker.make(
            Student,
            project_status=StudentProjectStatus.STUDYING,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student_with_group)
        response = api_client.get(
            "/api/dashboard/students/active_students_with_no_groups/",
        )
        assert response.status_code == status.HTTP_200_OK
        languages_and_levels = [
            {
                "id": language_and_level.pk,
                "language": language_and_level.language.name,
                "level": language_and_level.level.id,
            }
            for language_and_level in student.teaching_languages_and_levels.all()
        ]
        availability_slots = [
            {
                "id": slot.pk,
                "day_of_week_index": slot.day_of_week_index,
                "from_utc_hour": slot.time_slot.from_utc_hour.isoformat(),
                "to_utc_hour": slot.time_slot.to_utc_hour.isoformat(),
            }
            for slot in student.availability_slots.all()
        ]
        assert response.json() == [
            {
                "id": student.personal_info.id,
                "first_name": student.personal_info.first_name,
                "last_name": student.personal_info.last_name,
                "age_range": f"{student.age_range.age_from}-{student.age_range.age_to}",
                "teaching_languages_and_levels": languages_and_levels,
                "availability_slots": availability_slots,
                "comment": student.comment,
                "project_status": student.project_status.value,
                "situational_status": student.situational_status,
                "communication_language_mode": student.personal_info.communication_language_mode,
                "is_member_of_speaking_club": student.is_member_of_speaking_club,
                "utc_timedelta": f"UTC{sign}{utc_offset_hours:02}:{utc_offset_minutes:02}",
                "non_teaching_help_required": {
                    "career_strategy": False,
                    "career_switch": False,
                    "cv_proofread": False,
                    "cv_write_edit": False,
                    "job_search": False,
                    "linkedin": False,
                    "mock_interview": False,
                    "portfolio": False,
                    "translate_docs": False,
                    "uni_abroad": False,
                },
            }
        ]


class TestDashboardStudentAcceptedOfferedGroup:
    def test_general(self, api_client, availability_slots, timestamp, active_group: Group):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        coordinator = baker.make(
            Coordinator,
            make_m2m=True,
            _fill_optional=True,
        )
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/accepted_offered_group/",
            data={"group_id": active_group.pk, "coordinator_id": coordinator.pk},
        )
        student.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.STUDY_START
        assert log_event.to_group == active_group
        assert student.project_status == StudentProjectStatus.STUDYING
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

        coordinator_log_event = CoordinatorLogEvent.objects.filter(
            coordinator_id=coordinator.pk
        ).last()
        assert (
            coordinator_log_event.type == CoordinatorLogEventType.ADDED_STUDENT_TO_EXISTING_GROUP
        )
        assert_date_time_with_timestamp(coordinator_log_event.date_time, timestamp)

    def test_none_existing_group(self, api_client, availability_slots, active_group: Group):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        coordinator = baker.make(
            Coordinator,
            make_m2m=True,
            _fill_optional=True,
        )
        group_id = active_group.pk
        active_group.delete()
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/accepted_offered_group/",
            data={"group_id": group_id, "coordinator_id": coordinator.pk},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_student_already_in_group(self, api_client, availability_slots, active_group: Group):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        coordinator = baker.make(
            Coordinator,
            make_m2m=True,
            _fill_optional=True,
        )
        group_id = active_group.pk
        active_group.students.add(student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/accepted_offered_group/",
            data={"group_id": group_id, "coordinator_id": coordinator.pk},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_none_existing_coordinator(self, api_client, availability_slots, active_group: Group):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        coordinator = baker.make(
            Coordinator,
            make_m2m=True,
            _fill_optional=True,
        )
        group_id = active_group.pk
        coordinator_id = coordinator.pk
        coordinator.delete()
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/accepted_offered_group/",
            data={"group_id": group_id, "coordinator_id": coordinator_id},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDashboardStudentOfferJoinGroup:
    def test_general(self, api_client, active_group: Group, availability_slots, timestamp):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        prev_project_status = student.project_status
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/offer_join_group/",
            data={"group_id": active_group.pk},
        )
        student.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.GROUP_OFFERED
        assert log_event.to_group == active_group
        assert student.situational_status == StudentSituationalStatus.GROUP_OFFERED
        assert student.project_status == prev_project_status
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_student_already_in_group(self, api_client, active_group: Group, availability_slots):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.students.add(student)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/offer_join_group/",
            data={"group_id": active_group.pk},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_group_not_found(self, api_client, active_group: Group, availability_slots):
        student = baker.make(
            Student,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        group_id = active_group.pk
        active_group.delete()
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/offer_join_group/",
            data={"group_id": group_id},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_dashboard_student_left_project_prematurely(
    api_client, availability_slots, active_group: Group, timestamp
):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.students.add(student)
    response = api_client.post(
        f"/api/dashboard/students/{student.personal_info.id}/left_project_prematurely/",
    )
    student.refresh_from_db()
    active_group.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
    assert log_event.type == StudentLogEventType.LEFT_PREMATURELY
    assert student.project_status == StudentProjectStatus.LEFT_PREMATURELY
    assert student in active_group.students_former.all()
    assert student not in active_group.students.all()
    assert_date_time_with_timestamp(log_event.date_time, timestamp)


def test_dashboard_student_expelled(
    api_client, availability_slots, active_group: Group, timestamp
):
    student = baker.make(
        Student,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.students.add(student)
    response = api_client.post(
        f"/api/dashboard/students/{student.personal_info.id}/expelled/",
    )
    student.refresh_from_db()
    active_group.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
    assert log_event.type == StudentLogEventType.EXPELLED
    assert student.project_status == StudentProjectStatus.BANNED
    assert student in active_group.students_former.all()
    assert student not in active_group.students.all()
    assert_date_time_with_timestamp(log_event.date_time, timestamp)


class TestDashboardStudentCompletedOralInterview:
    def test_general_check(self, api_client, availability_slots, timestamp):
        student = baker.make(
            Student,
            teaching_languages_and_levels=[],
            project_status=StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        language_and_level = baker.make(LanguageAndLevel)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/completed_oral_interview/",
            data={"language_and_level_id": language_and_level.pk},
        )
        student.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: StudentLogEvent = StudentLogEvent.objects.filter(student_id=student.pk).last()
        assert log_event.type == StudentLogEventType.AWAITING_OFFER
        assert student.project_status == StudentProjectStatus.NO_GROUP_YET
        assert language_and_level in student.teaching_languages_and_levels.all()
        assert_date_time_with_timestamp(log_event.date_time, timestamp)
        assert_date_time_with_timestamp(student.status_since, timestamp)

    def test_wrong_project_status(self, api_client, availability_slots):
        student = baker.make(
            Student,
            teaching_languages_and_levels=[],
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        language_and_level = baker.make(LanguageAndLevel)
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/completed_oral_interview/",
            data={"language_and_level_id": language_and_level.pk},
        )
        if student.project_status == StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL:
            assert response.status_code == status.HTTP_204_NO_CONTENT
        else:
            assert response.status_code == status.HTTP_409_CONFLICT

    def test_wrong_language_and_level(self, api_client, availability_slots):
        student = baker.make(
            Student,
            teaching_languages_and_levels=[],
            make_m2m=True,
            project_status=StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        language_and_level = baker.make(LanguageAndLevel)
        language_pk = language_and_level.pk
        language_and_level.delete()
        response = api_client.post(
            f"/api/dashboard/students/{student.personal_info.id}/completed_oral_interview/",
            data={"language_and_level_id": language_pk},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
