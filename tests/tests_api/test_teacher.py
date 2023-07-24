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
from api.serializers import TeacherReadSerializer
from tests.tests_api.asserts import assert_response_data


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


def test_teacher_retrieve(api_client, availability_slots):
    teacher = baker.make(
        Teacher, make_m2m=True, _fill_optional=True, availability_slots=availability_slots
    )
    response = api_client.get(f"/api/teachers/{teacher.personal_info.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, TeacherReadSerializer(teacher).data)


# TODO: Add tests for update (+ decide PUT or PATCH?)
