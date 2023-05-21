import pytz
from model_bakery import baker
from rest_framework import status

from api.models import LanguageAndLevel, PersonalInfo, TeacherUnder18
from api.models.choices.statuses import TeacherUnder18Status


def test_teacher_under_18_create(api_client, faker):
    initial_count = TeacherUnder18.objects.count()
    personal_info = baker.make(PersonalInfo)

    teaching_languages_and_levels_ids = [
        LanguageAndLevel.objects.first().id,
        LanguageAndLevel.objects.last().id,
    ]

    data = {
        "personal_info": personal_info.id,
        "can_host_speaking_club": faker.pybool(),
        "comment": faker.text(),
        "status": TeacherUnder18Status.ACTIVE.value,
        "status_since": faker.date_time(tzinfo=pytz.utc),
        "teaching_languages_and_levels": teaching_languages_and_levels_ids,
        "has_hosted_speaking_club": faker.pybool(),
        "is_validated": faker.pybool(),
        "non_teaching_help_provided_comment": faker.text(),
    }
    response = api_client.post("/api/teachers_under_18/", data=data)
    assert response.status_code == status.HTTP_201_CREATED

    assert TeacherUnder18.objects.count() == initial_count + 1

    m2m_fields = ["teaching_languages_and_levels"]
    # Changing for further filtering
    for field in m2m_fields:
        data[f"{field}__in"] = data.pop(field)

    assert TeacherUnder18.objects.filter(**data).exists()


def test_teacher_under_18_retrieve(api_client):
    teacher_under_18 = baker.make(TeacherUnder18)

    languages_and_levels = [
        {
            "id": language_and_level.id,
            "language": {
                "id": language_and_level.language.id,
                "name": language_and_level.language.name,
            },
            "level": language_and_level.level.id,
        }
        for language_and_level in teacher_under_18.teaching_languages_and_levels.all()
    ]

    response = api_client.get(f"/api/teachers_under_18/{teacher_under_18.personal_info.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "personal_info": teacher_under_18.personal_info.id,
        "comment": teacher_under_18.comment,
        "can_host_speaking_club": teacher_under_18.can_host_speaking_club,
        "teaching_languages_and_levels": languages_and_levels,
        "status": teacher_under_18.status,
        "status_since": teacher_under_18.status_since.isoformat().replace("+00:00", "Z"),
        "has_hosted_speaking_club": teacher_under_18.has_hosted_speaking_club,
        "is_validated": teacher_under_18.is_validated,
        "non_teaching_help_provided_comment": teacher_under_18.non_teaching_help_provided_comment,
    }
