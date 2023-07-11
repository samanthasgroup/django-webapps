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
        "status": teacher.status,
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


# TODO: Add tests for update (+ decide PUT or PATCH?)
