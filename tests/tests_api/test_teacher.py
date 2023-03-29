from model_bakery import baker
from rest_framework import status

from api.models import AgeRange, DayAndTimeSlot, LanguageAndLevel, PersonalInfo, Teacher


def test_teacher_create(api_client, faker):
    initial_count = Teacher.objects.count()
    personal_info = baker.make(PersonalInfo)
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
    data = {
        "personal_info": personal_info.id,
        "student_age_ranges": age_range_ids,
        "teaching_languages_and_levels": teaching_languages_and_levels_ids,
        "availability_slots": availability_slots_ids,
        "comment": faker.text(),
        "can_help_with_cv": faker.pybool(),
        "can_check_syllabus": faker.pybool(),
        "can_consult_other_teachers": faker.pybool(),
        "can_give_feedback": faker.pybool(),
        "can_help_with_children_group": faker.pybool(),
        "can_help_with_materials": faker.pybool(),
        "can_invite_to_class": faker.pybool(),
        "can_work_in_tandem": faker.pybool(),
        "has_prior_teaching_experience": faker.pybool(),
        "simultaneous_groups": faker.pyint(),
        "weekly_frequency_per_group": faker.pyint(),
        "additional_skills_comment": faker.text(),
        "can_help_with_speaking_club": faker.pybool(),
    }
    response = api_client.post("/api/teachers/", data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Teacher.objects.count() == initial_count + 1

    m2m_fields = ["teaching_languages_and_levels", "availability_slots", "student_age_ranges"]
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert Teacher.objects.filter(**data).exists()


def test_teacher_retrieve(api_client):
    teacher = baker.make(Teacher, make_m2m=True)
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
    assert response_json == {
        "personal_info": teacher.personal_info.id,
        "student_age_ranges": age_ranges,
        "teaching_languages_and_levels": languages_and_levels,
        "availability_slots": availability_slots,
        "comment": teacher.comment,
        "status": teacher.status,
        "can_help_with_cv": teacher.can_help_with_cv,
        "can_check_syllabus": teacher.can_check_syllabus,
        "can_consult_other_teachers": teacher.can_consult_other_teachers,
        "can_give_feedback": teacher.can_give_feedback,
        "can_help_with_children_group": teacher.can_help_with_children_group,
        "can_help_with_materials": teacher.can_help_with_materials,
        "can_invite_to_class": teacher.can_invite_to_class,
        "can_work_in_tandem": teacher.can_work_in_tandem,
        "has_prior_teaching_experience": teacher.has_prior_teaching_experience,
        "simultaneous_groups": teacher.simultaneous_groups,
        "weekly_frequency_per_group": teacher.weekly_frequency_per_group,
        "additional_skills_comment": teacher.additional_skills_comment,
        "can_help_with_speaking_club": teacher.can_help_with_speaking_club,
    }


# TODO: Add tests for update (+ decide PUT or PATCH?)
