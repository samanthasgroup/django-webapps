from rest_framework import status

from api.models import Group, StudentLogEvent, TeacherLogEvent
from api.models.choices.log_event_type import StudentLogEventType, TeacherLogEventType
from api.models.choices.status import GroupStatus, StudentStatus, TeacherStatus
from api.serializers import GroupWriteSerializer
from tests.tests_api.test_group import compare_date_time_with_timestamp


class TestGroupCreation:
    def get_data(self, group: Group):
        return {
            "lesson_duration_in_minutes": 30,
            "communication_language_mode": group.communication_language_mode,
            "availability_slots_for_auto_matching": [
                a.id for a in group.availability_slots_for_auto_matching.iterator()
            ],
            "language_and_level": group.language_and_level.id,
            "monday": "10:00:00",
            "coordinators": [c.pk for c in group.coordinators.iterator()],
            "students": [s.pk for s in group.students.iterator()],
            "teachers": [t.pk for t in group.teachers.iterator()],
        }

    def test_group_create_general(self, api_client, group: Group, timestamp):
        data = self.get_data(group)
        response = api_client.post("/api/groups/", data)
        assert response.status_code == status.HTTP_201_CREATED
        created_group = Group.objects.get(id=response.data["id"])
        serializer = GroupWriteSerializer(created_group)
        for k, v in data.items():
            assert v == response.data[k]
            assert v == serializer.data[k]

        assert group.status == GroupStatus.PENDING

        common_status_since = created_group.status_since
        compare_date_time_with_timestamp(common_status_since, timestamp)

        for student in group.students.iterator():
            assert student.status == StudentStatus.GROUP_OFFERED
            assert student.status_since == common_status_since
            log_event: StudentLogEvent = StudentLogEvent.objects.get(student_id=student.pk)
            assert log_event.type == StudentLogEventType.GROUP_OFFERED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)

        for teacher in group.teachers.iterator():
            assert teacher.status == TeacherStatus.GROUP_OFFERED
            assert teacher.status_since == common_status_since
            log_event: TeacherLogEvent = TeacherLogEvent.objects.get(teacher_id=teacher.pk)
            assert log_event.type == TeacherLogEventType.GROUP_OFFERED
            compare_date_time_with_timestamp(log_event.date_time, timestamp)
