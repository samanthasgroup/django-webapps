import pytz
from model_bakery import baker
from rest_framework import status

from api.models import (
    AgeRange,
    DayAndTimeSlot,
    LanguageAndLevel,
    NonTeachingHelp,
    PersonalInfo,
    Student,
)


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
    non_teaching_help_ids = [
        NonTeachingHelp.objects.first().id,
        NonTeachingHelp.objects.last().id,
    ]
    data = {
        "personal_info": personal_info.id,
        "comment": faker.text(),
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
        "status_since": student.status_since.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "is_member_of_speaking_club": student.is_member_of_speaking_club,
        "can_read_in_english": student.can_read_in_english,
        # These are optional, so baker won't generate them (unless _fill_optional is True)
        "non_teaching_help_required": [],
        "smalltalk_test_result": None,
    }


# TODO: Add tests for update (+ decide PUT or PATCH?)
