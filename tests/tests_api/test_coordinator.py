import pytz
from model_bakery import baker, seq
from rest_framework import status

from api.models import Coordinator, PersonalInfo
from api.models.choices.log_event_type import CoordinatorLogEventType
from api.models.choices.status.project import CoordinatorProjectStatus
from api.models.log_event import CoordinatorLogEvent
from tests.tests_api.asserts import assert_date_time_with_timestamp


def test_coordinator_create(api_client, faker, timestamp):
    mentor = baker.make(Coordinator)
    initial_count = Coordinator.objects.count()
    personal_info = baker.make(PersonalInfo, first_name=seq("Ivan"))
    data = {
        "personal_info": personal_info.pk,
        "comment": faker.text(),
        "status_since": faker.date_time(tzinfo=pytz.timezone("Europe/Berlin")),
        "additional_skills_comment": faker.text(),
        "is_admin": faker.pybool(),
        "is_validated": faker.pybool(),
        "project_status": CoordinatorProjectStatus.WORKING_OK,
        "situational_status": "",
        "mentor": mentor.pk,
    }
    response = api_client.post("/api/coordinators/", data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Coordinator.objects.count() == initial_count + 1
    assert Coordinator.objects.filter(**data).exists()

    log_event = CoordinatorLogEvent.objects.filter(coordinator_id=personal_info.id).last()
    assert log_event.type == CoordinatorLogEventType.APPLIED
    assert_date_time_with_timestamp(log_event.date_time, timestamp)
