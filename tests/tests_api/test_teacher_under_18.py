import pytz
from model_bakery import baker, seq
from rest_framework import status

from api.models import LanguageAndLevel, PersonalInfo, TeacherUnder18
from api.models.choices.status import TeacherUnder18Status
from api.serializers import TeacherUnder18ReadSerializer
from tests.tests_api.asserts import assert_response_data


def test_teacher_under_18_create(api_client, faker):
    initial_count = TeacherUnder18.objects.count()
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))

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

    response = api_client.get(f"/api/teachers_under_18/{teacher_under_18.personal_info.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert_response_data(response.data, TeacherUnder18ReadSerializer(teacher_under_18).data)
