from model_bakery import baker
from rest_framework import status

from api.models import Group
from api.models.choices.statuses import StudentStatus


def test_public_group_list(api_client):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    response = api_client.get("/api/public/groups/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json == [
        {
            "id": group.pk,
            "communication_language_mode": group.communication_language_mode,
            "monday": str(group.monday),
            "tuesday": str(group.tuesday),
            "wednesday": str(group.wednesday),
            "thursday": str(group.thursday),
            "friday": str(group.friday),
            "saturday": str(group.saturday),
            "sunday": str(group.sunday),
            "language_and_level": {
                "language": group.language_and_level.language.name,
                "level": group.language_and_level.level.id,
            },
            "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
            "status": group.status,
            "start_date": group.start_date.isoformat(),
            "end_date": group.end_date.isoformat(),
            "telegram_chat_url": group.telegram_chat_url,
            "coordinators": [
                {
                    "id": coordinator.pk,
                    "full_name": coordinator.personal_info.full_name,
                }
                for coordinator in group.coordinators.all()
            ],
            "teachers": [
                {
                    "id": teacher.pk,
                    "full_name": teacher.personal_info.full_name,
                }
                for teacher in group.teachers.all()
            ],
            "students_count": group.students.count(),
            "is_for_staff_only": group.is_for_staff_only,
        }
    ]


def test_public_group_retrieve(api_client):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    response = api_client.get(f"/api/public/groups/{group.pk}/")

    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json == {
        "id": group.pk,
        "communication_language_mode": group.communication_language_mode,
        "monday": str(group.monday),
        "tuesday": str(group.tuesday),
        "wednesday": str(group.wednesday),
        "thursday": str(group.thursday),
        "friday": str(group.friday),
        "saturday": str(group.saturday),
        "sunday": str(group.sunday),
        "language_and_level": {
            "language": group.language_and_level.language.name,
            "level": group.language_and_level.level.id,
        },
        "lesson_duration_in_minutes": group.lesson_duration_in_minutes,
        "status": group.status,
        "start_date": group.start_date.isoformat(),
        "end_date": group.end_date.isoformat(),
        "telegram_chat_url": group.telegram_chat_url,
        "coordinators": [
            {
                "id": coordinator.pk,
                "full_name": coordinator.personal_info.full_name,
            }
            for coordinator in group.coordinators.all()
        ],
        "teachers": [
            {
                "id": teacher.pk,
                "full_name": teacher.personal_info.full_name,
            }
            for teacher in group.teachers.all()
        ],
        "students": [
            {
                "id": student.pk,
                "full_name": student.personal_info.full_name,
            }
            for student in group.students.all()
        ],
        "is_for_staff_only": group.is_for_staff_only,
    }


def test_public_group_start(api_client):
    group = baker.make(Group, _fill_optional=True, make_m2m=True)

    group.students.update(status=StudentStatus.AWAITING_START)

    response = api_client.post(f"/api/public/groups/{group.id}/start/")
    assert response.status_code == status.HTTP_201_CREATED

    for student in group.students.iterator():
        assert student.status == StudentStatus.STUDYING
