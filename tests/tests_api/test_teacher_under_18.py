from model_bakery import baker
from rest_framework import status

from api.models import PersonalInfo, TeacherUnder18
from api.models.constants import DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH


def test_teacher_under_18_create(api_client, faker):
    initial_count = TeacherUnder18.objects.count()
    personal_info = baker.make(PersonalInfo)

    data = {
        "personal_info": personal_info.id,
        "additional_skills_comment": faker.pystr(max_chars=DEFAULT_CHOICE_CHAR_FIELD_MAX_LENGTH),
        "can_help_with_speaking_club": faker.pybool(),
    }
    response = api_client.post("/api/teachers_under_18/", data=data)
    assert response.status_code == status.HTTP_201_CREATED

    assert TeacherUnder18.objects.count() == initial_count + 1
    assert TeacherUnder18.objects.filter(**data).exists()


def test_teacher_under_18_retrieve(api_client):
    teacher_under_18 = baker.make(TeacherUnder18)

    response = api_client.get(f"/api/teachers_under_18/{teacher_under_18.personal_info.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "personal_info": teacher_under_18.personal_info.id,
        "comment": teacher_under_18.comment,
        "additional_skills_comment": teacher_under_18.additional_skills_comment,
        "can_help_with_speaking_club": teacher_under_18.can_help_with_speaking_club,
        "status": teacher_under_18.status,
    }
