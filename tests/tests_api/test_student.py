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
    Student,
)
from api.models.choices.status import StudentProjectStatus


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
        "project_status": StudentProjectStatus.NOT_STUDYING.value,
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
        "status_since": student.status_since.isoformat().replace("+00:00", "Z"),
        "is_member_of_speaking_club": student.is_member_of_speaking_club,
        "can_read_in_english": student.can_read_in_english,
        # These are optional, so baker won't generate them (unless _fill_optional is True)
        "non_teaching_help_required": [],
        "smalltalk_test_result": None,
    }


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


# TODO: Add tests for update (+ decide PUT or PATCH?)
