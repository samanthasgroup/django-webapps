import datetime

import pytz
from model_bakery import baker, seq
from rest_framework import status

from api.models import (
    AgeRange,
    DayAndTimeSlot,
    LanguageAndLevel,
    NonTeachingHelp,
    PersonalInfo,
    Teacher,
)
from api.models.choices.status import TeacherStatus
from api.serializers import (
    DashboardTeacherSerializer,
    TeacherReadSerializer,
    TeacherWriteSerializer,
)
from tests.tests_api.asserts import assert_response_data, assert_response_data_list


def test_teacher_create(api_client, faker):
    initial_count = Teacher.objects.count()
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
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
        "teaching_languages_and_levels": teaching_languages_and_levels_ids,
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
        "status": TeacherStatus.AWAITING_OFFER.value,
        "status_since": faker.date_time(tzinfo=pytz.utc),
        "has_hosted_speaking_club": faker.pybool(),
        "is_validated": faker.pybool(),
        "non_teaching_help_provided": non_teaching_help_ids,
        "non_teaching_help_provided_comment": faker.text(),
    }
    response = api_client.post("/api/teachers/", data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Teacher.objects.count() == initial_count + 1

    m2m_fields = [
        "teaching_languages_and_levels",
        "availability_slots",
        "student_age_ranges",
        "non_teaching_help_provided",
    ]
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert Teacher.objects.filter(**data).exists()


def test_teacher_update(api_client, faker, availability_slots):
    teacher = baker.make(
        Teacher,
        make_m2m=True,
        _fill_optional=True,
        availability_slots=availability_slots,
    )
    fields_to_update = {
        "weekly_frequency_per_group": faker.pyint(min_value=1, max_value=12),
        "status": TeacherStatus.BANNED,
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
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, TeacherReadSerializer(teacher).data)


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


def test_dashboard_teache_list(api_client, faker, availability_slots):
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
