import datetime

import pytest
import pytz
from model_bakery import baker, seq
from rest_framework import status

from api.models import (
    AgeRange,
    Coordinator,
    DayAndTimeSlot,
    Group,
    LanguageAndLevel,
    NonTeachingHelp,
    PersonalInfo,
    Teacher,
)
from api.models.choices.log_event_type import TeacherLogEventType
from api.models.choices.status import TeacherProjectStatus
from api.models.log_event import TeacherLogEvent
from api.serializers import DashboardTeacherSerializer, TeacherWriteSerializer
from tests.tests_api.asserts import (
    assert_date_time_with_timestamp,
    assert_response_data,
    assert_response_data_list,
)


@pytest.mark.parametrize(
    "include_language_and_level",
    [True, False],
)
def test_teacher_create(api_client, faker, timestamp, include_language_and_level):
    initial_count = Teacher.objects.count()
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
    teaching_languages_and_levels_ids = []
    if include_language_and_level:
        teaching_languages_and_levels_ids = [
            LanguageAndLevel.objects.first().id,
            LanguageAndLevel.objects.last().id,
        ]
    availability_slots_ids = [
        DayAndTimeSlot.objects.first().id,
        DayAndTimeSlot.objects.last().id,
    ]
    age_range_ids = [
        AgeRange.objects.first().id,
        AgeRange.objects.last().id,
    ]
    non_teaching_help_ids = [
        NonTeachingHelp.objects.first().id,
        NonTeachingHelp.objects.last().id,
    ]
    data = {
        "personal_info": personal_info.id,
        "student_age_ranges": age_range_ids,
        "availability_slots": availability_slots_ids,
        "comment": faker.text(),
        "peer_support_can_check_syllabus": faker.pybool(),
        "peer_support_can_host_mentoring_sessions": faker.pybool(),
        "peer_support_can_give_feedback": faker.pybool(),
        "peer_support_can_help_with_childrens_groups": faker.pybool(),
        "peer_support_can_provide_materials": faker.pybool(),
        "peer_support_can_invite_to_class": faker.pybool(),
        "peer_support_can_work_in_tandem": faker.pybool(),
        "has_prior_teaching_experience": faker.pybool(),
        "simultaneous_groups": faker.pyint(),
        "weekly_frequency_per_group": faker.pyint(),
        "can_host_speaking_club": faker.pybool(),
        "project_status": TeacherProjectStatus.NO_GROUP_YET.value,
        "situational_status": "",
        "status_since": faker.date_time(tzinfo=pytz.utc),
        "has_hosted_speaking_club": faker.pybool(),
        "is_validated": faker.pybool(),
        "non_teaching_help_provided": non_teaching_help_ids,
        "non_teaching_help_provided_comment": faker.text(),
    }
    if include_language_and_level:
        data["teaching_languages_and_levels"] = teaching_languages_and_levels_ids
    response = api_client.post("/api/teachers/", data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Teacher.objects.count() == initial_count + 1

    m2m_fields = [
        "availability_slots",
        "student_age_ranges",
        "non_teaching_help_provided",
    ]
    if include_language_and_level:
        m2m_fields.append("teaching_languages_and_levels")
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert Teacher.objects.filter(**data).exists()
    if include_language_and_level:
        log_events = TeacherLogEvent.objects.filter(teacher_id=personal_info.id)
        assert log_events[0].type == TeacherLogEventType.REGISTERED
        assert_date_time_with_timestamp(log_events[0].date_time, timestamp)
        assert log_events[1].type == TeacherLogEventType.AWAITING_OFFER
        assert_date_time_with_timestamp(log_events[1].date_time, timestamp)
    else:
        log_event = TeacherLogEvent.objects.filter(teacher_id=personal_info.id).last()
        assert log_event.type == TeacherLogEventType.REGISTERED
        assert_date_time_with_timestamp(log_event.date_time, timestamp)


def test_teacher_update(api_client, faker, availability_slots):
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    fields_to_update = {
        "weekly_frequency_per_group": faker.pyint(min_value=1, max_value=12),
        "project_status": TeacherProjectStatus.BANNED,
        "has_prior_teaching_experience": True,
        "availability_slots": [i.id for i in availability_slots[1:3]],
    }

    response = api_client.patch(
        f"/api/teachers/{teacher.personal_info.id}/", data=fields_to_update
    )
    teacher_data = TeacherWriteSerializer(teacher).data
    for field, val in fields_to_update.items():
        teacher_data[field] = val
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, teacher_data)

    db_teacher = Teacher.objects.get(pk=teacher.pk)
    db_teacher_data = TeacherWriteSerializer(db_teacher).data
    assert_response_data(db_teacher_data, teacher_data)


def test_teacher_retrieve(api_client, availability_slots):
    teacher = baker.make(
        Teacher, make_m2m=True, _fill_optional=True, availability_slots=availability_slots
    )
    response = api_client.get(f"/api/teachers/{teacher.personal_info.id}/")

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
        for language_and_level in teacher.teaching_languages_and_levels.all()
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
        for slot in teacher.availability_slots.all()
    ]
    age_ranges = [
        {
            "id": age_range.id,
            "age_from": age_range.age_from,
            "age_to": age_range.age_to,
            "type": age_range.type,
        }
        for age_range in teacher.student_age_ranges.all()
    ]
    non_teaching_help = [
        {
            "id": item.id,
            "name": item.name,
        }
        for item in teacher.non_teaching_help_provided.all()
    ]
    assert response_json == {
        "personal_info": teacher.personal_info.id,
        "student_age_ranges": age_ranges,
        "teaching_languages_and_levels": languages_and_levels,
        "availability_slots": availability_slots,
        "comment": teacher.comment,
        "project_status": teacher.project_status,
        "situational_status": teacher.situational_status,
        "status_since": teacher.status_since.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "peer_support_can_check_syllabus": teacher.peer_support_can_check_syllabus,
        "peer_support_can_host_mentoring_sessions": teacher.peer_support_can_host_mentoring_sessions,  # noqa E501
        "peer_support_can_give_feedback": teacher.peer_support_can_give_feedback,
        "peer_support_can_help_with_childrens_groups": teacher.peer_support_can_help_with_childrens_groups,  # noqa E501
        "peer_support_can_provide_materials": teacher.peer_support_can_provide_materials,
        "peer_support_can_invite_to_class": teacher.peer_support_can_invite_to_class,
        "peer_support_can_work_in_tandem": teacher.peer_support_can_work_in_tandem,
        "has_prior_teaching_experience": teacher.has_prior_teaching_experience,
        "simultaneous_groups": teacher.simultaneous_groups,
        "weekly_frequency_per_group": teacher.weekly_frequency_per_group,
        "can_host_speaking_club": teacher.can_host_speaking_club,
        "has_hosted_speaking_club": teacher.has_hosted_speaking_club,
        "is_validated": teacher.is_validated,
        "non_teaching_help_provided": non_teaching_help,
        "non_teaching_help_provided_comment": teacher.non_teaching_help_provided_comment,
    }


def test_dashboard_teacher_retrieve(api_client, faker, availability_slots):
    utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
    sign = "+" if utc_offset_hours >= 0 else "-"
    utc_offset_minutes = faker.random_element([0, 30])
    utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        personal_info__utc_timedelta=utc_timedelta,
        availability_slots=availability_slots,
    )
    response = api_client.get(f"/api/dashboard/teachers/{teacher.personal_info.id}/")

    assert response.status_code == status.HTTP_200_OK
    teacher_data = DashboardTeacherSerializer(teacher).data

    teacher_data["utc_timedelta"] = f"UTC{sign}{utc_offset_hours:02}:{utc_offset_minutes:02}"
    assert_response_data(response.data, teacher_data)


def test_dashboard_teacher_list(api_client, faker, availability_slots):
    utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
    sign = "+" if utc_offset_hours >= 0 else "-"
    utc_offset_minutes = faker.random_element([0, 30])
    utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        personal_info__utc_timedelta=utc_timedelta,
        availability_slots=availability_slots,
    )
    response = api_client.get("/api/dashboard/teachers/")

    assert response.status_code == status.HTTP_200_OK
    teacher_data = DashboardTeacherSerializer(teacher).data
    teacher_data["utc_timedelta"] = f"UTC{sign}{utc_offset_hours:02}:{utc_offset_minutes:02}"
    assert_response_data_list(response.data, [teacher_data])


class TestDashboardTeacherTransfer:
    def test_dashboard_teacher_transfer_general_check(
        self, api_client, active_group: Group, timestamp, availability_slots
    ):
        teacher = baker.make(
            Teacher,
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
        old_group.teachers.add(teacher)
        old_group.save()
        response = api_client.post(
            f"/api/dashboard/teachers/{teacher.personal_info.id}/transfer/",
            data={"to_group_id": active_group.pk, "from_group_id": old_group.pk},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        teacher.refresh_from_db()
        current_teacher_groups = teacher.groups.all()
        assert len(current_teacher_groups) == 1
        assert current_teacher_groups[0] == active_group
        assert teacher in old_group.teachers_former.all()
        assert teacher not in old_group.teachers.all()
        log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
        assert log_event.type == TeacherLogEventType.TRANSFERRED
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    def test_dashboard_teacher_transfer_from_empty_group(
        self, api_client, active_group: Group, availability_slots
    ):
        teacher = baker.make(
            Teacher,
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
            f"/api/dashboard/teachers/{teacher.personal_info.id}/transfer/",
            data={"to_group_id": active_group.pk, "from_group_id": old_group.pk},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_dashboard_teacher_transfer_to_none_exsiting_group(
        self, api_client, active_group: Group, availability_slots
    ):
        teacher = baker.make(
            Teacher,
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
        group_id = active_group.pk
        active_group.delete()
        response = api_client.post(
            f"/api/dashboard/teachers/{teacher.personal_info.id}/transfer/",
            data={"to_group_id": group_id, "from_group_id": old_group.pk},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDashboardTeacherWithPersonalInfo:
    def test_can_filter_by_coordinator_email(self, api_client, faker, availability_slots):
        utc_offset_hours = faker.pyint(min_value=-12, max_value=12)
        utc_offset_minutes = faker.random_element([0, 30])
        utc_timedelta = datetime.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes)
        teacher = baker.make(
            Teacher,
            make_m2m=True,
            personal_info__utc_timedelta=utc_timedelta,
            availability_slots=availability_slots,
        )

        other_teacher = baker.make(
            Teacher,
            make_m2m=True,
            personal_info__utc_timedelta=utc_timedelta,
            availability_slots=availability_slots,
        )  # This teacher is not in the group and should not be included in the response.
        coordinator = baker.make(Coordinator, make_m2m=True, _fill_optional=True)
        group = baker.make(
            Group,
            _fill_optional=True,
            make_m2m=True,
            availability_slots_for_auto_matching=availability_slots,
        )
        group.teachers.add(teacher)
        group.coordinators.add(coordinator)

        response = api_client.get(
            "/api/dashboard/teachers_with_personal_info/",
            data={"for_coordinator_email": coordinator.personal_info.email},
        )
        assert response.status_code == status.HTTP_200_OK

        returned_ids = [teacher["id"] for teacher in response.json()]

        assert teacher.personal_info.id in returned_ids
        assert other_teacher.personal_info.id not in returned_ids

    @pytest.mark.parametrize("project_status", TeacherProjectStatus.values)
    def test_can_filter_by_project_status(self, api_client, availability_slots, project_status):
        group = baker.make(
            Group,
            make_m2m=True,
            _fill_optional=True,
            availability_slots_for_auto_matching=availability_slots,
        )

        teachers = [
            baker.make(
                Teacher,
                make_m2m=True,
                personal_info__utc_timedelta=datetime.timedelta(),
                availability_slots=availability_slots,
                project_status=ps,
            )
            for ps in TeacherProjectStatus.values
        ]

        group.teachers.add(*teachers)

        response = api_client.get(
            "/api/dashboard/teachers_with_personal_info/",
            data={"project_status": project_status},
        )

        assert response.status_code == status.HTTP_200_OK

        returned_statuses = [teacher["project_status"] for teacher in response.json()]

        assert all(returned_status == project_status for returned_status in returned_statuses)


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/dashboard/teachers/",
        "/api/teachers/",
    ],
)
def test_dashboard_teacher_went_on_leave(api_client, availability_slots, timestamp, endpoint):
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    response = api_client.post(
        f"{endpoint}{teacher.personal_info.id}/went_on_leave/",
    )
    teacher.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: TeacherLogEvent = TeacherLogEvent.objects.filter(teacher_id=teacher.pk).last()
    assert log_event.type == TeacherLogEventType.GONE_ON_LEAVE
    assert teacher.project_status == TeacherProjectStatus.ON_LEAVE
    assert_date_time_with_timestamp(log_event.date_time, timestamp)


class TestDashboardTeacherReturnedFromLeave:
    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/dashboard/teachers/",
            "/api/teachers/",
        ],
    )
    def test_no_group(self, api_client, availability_slots, timestamp, endpoint):
        teacher = baker.make(
            Teacher,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        response = api_client.post(
            f"{endpoint}{teacher.personal_info.id}/returned_from_leave/",
        )
        teacher.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: TeacherLogEvent = TeacherLogEvent.objects.filter(teacher_id=teacher.pk).last()
        assert log_event.type == TeacherLogEventType.RETURNED_FROM_LEAVE
        assert teacher.project_status == TeacherProjectStatus.NO_GROUP_YET
        assert_date_time_with_timestamp(log_event.date_time, timestamp)

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/dashboard/teachers/",
            "/api/teachers/",
        ],
    )
    def test_with_group(  # noqa: PLR0913
        self, api_client, availability_slots, timestamp, active_group, endpoint
    ):
        teacher = baker.make(
            Teacher,
            make_m2m=True,
            _fill_optional=True,
            availability_slots=availability_slots,
        )
        active_group.teachers.add(teacher)
        active_group.save()
        response = api_client.post(
            f"{endpoint}{teacher.personal_info.id}/returned_from_leave/",
        )
        teacher.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        log_event: TeacherLogEvent = TeacherLogEvent.objects.filter(teacher_id=teacher.pk).last()
        assert log_event.type == TeacherLogEventType.RETURNED_FROM_LEAVE
        assert teacher.project_status == TeacherProjectStatus.WORKING
        assert_date_time_with_timestamp(log_event.date_time, timestamp)


def test_dashboard_teacher_left_project_prematurely(
    api_client, availability_slots, active_group: Group, timestamp
):
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.teachers.add(teacher)
    response = api_client.post(
        f"/api/dashboard/teachers/{teacher.personal_info.id}/left_project_prematurely/",
    )
    teacher.refresh_from_db()
    active_group.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: TeacherLogEvent = TeacherLogEvent.objects.filter(teacher_id=teacher.pk).last()
    assert log_event.type == TeacherLogEventType.LEFT_PREMATURELY
    assert teacher.project_status == TeacherProjectStatus.LEFT_PREMATURELY
    assert teacher in active_group.teachers_former.all()
    assert teacher not in active_group.teachers.all()
    assert_date_time_with_timestamp(log_event.date_time, timestamp)


def test_dashboard_teacher_expelled(
    api_client, availability_slots, active_group: Group, timestamp
):
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    active_group.teachers.add(teacher)
    response = api_client.post(
        f"/api/dashboard/teachers/{teacher.personal_info.id}/expelled/",
    )
    teacher.refresh_from_db()
    active_group.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    log_event: TeacherLogEvent = TeacherLogEvent.objects.filter(teacher_id=teacher.pk).last()
    assert log_event.type == TeacherLogEventType.EXPELLED
    assert teacher.project_status == TeacherProjectStatus.BANNED
    assert teacher in active_group.teachers_former.all()
    assert teacher not in active_group.teachers.all()
    assert_date_time_with_timestamp(log_event.date_time, timestamp)
