from model_bakery import baker
from rest_framework import status

from api.models import AgeRange, DayAndTimeSlot, LanguageAndLevel, PersonalInfo, Student


def test_student_create(api_client, faker):
    initial_count = Student.objects.count()
    personal_info = baker.make(PersonalInfo)
    age_range_id = AgeRange.objects.first().id
    teaching_languages_and_levels_ids = [
        LanguageAndLevel.objects.first().id,
        LanguageAndLevel.objects.last().id,
    ]
    availability_slots_ids = [
        DayAndTimeSlot.objects.first().id,
        DayAndTimeSlot.objects.last().id,
    ]
    data = {
        "personal_info": personal_info.id,
        "age_range": age_range_id,
        "teaching_languages_and_levels": teaching_languages_and_levels_ids,
        "is_member_of_speaking_club": faker.pybool(),
        "requires_help_with_cv": faker.pybool(),
        "availability_slots": availability_slots_ids,
    }
    response = api_client.post("/api/students/", data=data)

    # TODO why does the test NOT fail when we pass no status and DOES fail when I pass one
    #  (as "status": faker.random_element(Student.Status.values)? The test for Teacher fails
    #  if I pass no status.  There is something wrong with Student and I can't figure out what.
    #  BTW I think we should assign a default status at creation for all Person submodels.

    assert response.status_code == status.HTTP_201_CREATED
    assert Student.objects.count() == initial_count + 1

    m2m_fields = [
        "teaching_languages_and_levels",
        "availability_slots",
    ]  # TODO children
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert Student.objects.filter(**data).exists()


def test_student_retrieve(api_client):
    student = baker.make(Student, make_m2m=True)
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
        "status": student.status,
        "is_member_of_speaking_club": student.is_member_of_speaking_club,
        "requires_help_with_cv": student.requires_help_with_cv,
        "smalltalk_test_result": None,
    }


# TODO: Add tests for update (+ decide PUT or PATCH?)
