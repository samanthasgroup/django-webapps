from datetime import timedelta

import pytest
from django.utils import timezone
from pytest_mock import MockerFixture

from alerts.handlers.coordinator import CoordinatorOverdueLeaveHandler
from alerts.handlers.teacher import TeacherNoGroup45DaysHandler
from alerts.models import Alert
from alerts.tasks import check_system_alerts
from alerts.utils import create_alert_for_object, resolve_alerts_for_objects
from api.models.choices.log_event_type import CoordinatorLogEventType, TeacherLogEventType
from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage
from api.models.choices.status import TeacherProjectStatus
from api.models.choices.status.project import CoordinatorProjectStatus
from api.models.coordinator import Coordinator
from api.models.log_event import CoordinatorLogEvent, TeacherLogEvent
from api.models.personal_info import PersonalInfo
from api.models.teacher import Teacher


@pytest.fixture  # type: ignore[misc]
def personal_info() -> PersonalInfo:
    """Базовая PersonalInfo для тестов."""
    return PersonalInfo.objects.create(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        information_source="test",
        registration_telegram_bot_language=RegistrationTelegramBotLanguage.EN,
    )


@pytest.fixture  # type: ignore[misc]
def teacher_no_group(personal_info: PersonalInfo) -> Teacher:
    """Учитель со статусом NO_GROUP_YET."""
    return Teacher.objects.create(
        personal_info=personal_info,
        project_status=TeacherProjectStatus.NO_GROUP_YET,
        status_since=timezone.now(),
        is_validated=False,
        weekly_frequency_per_group=1,
    )


@pytest.fixture  # type: ignore[misc]
def coordinator_on_leave(personal_info: PersonalInfo) -> Coordinator:
    """Координатор в отпуске."""
    return Coordinator.objects.create(
        personal_info=personal_info,
        project_status=CoordinatorProjectStatus.ON_LEAVE,
        is_validated=False,
        status_since=timezone.now(),
    )


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_no_group_creates_alert(teacher_no_group: Teacher) -> None:
    """Handler должен создать алерт, если учитель ждёт > 45 дней."""
    teacher = teacher_no_group
    past = timezone.now() - timedelta(days=46)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.AWAITING_OFFER,
        comment="",
        date_time=past,
    )

    handler = TeacherNoGroup45DaysHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_no_group_no_alert_for_recent_event(teacher_no_group: Teacher) -> None:
    """Не должен появляться алерт, если событие свежее порога."""
    teacher = teacher_no_group
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.AWAITING_OFFER,
        comment="",
        date_time=timezone.now(),
    )

    handler = TeacherNoGroup45DaysHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_no_group_resolves_after_status_change(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    past = timezone.now() - timedelta(days=46)
    TeacherLogEvent.objects.create(
        teacher=teacher, type=TeacherLogEventType.AWAITING_OFFER, comment="", date_time=past
    )

    handler = TeacherNoGroup45DaysHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    # меняем статус -> алерт должен резолвиться
    teacher.project_status = TeacherProjectStatus.WORKING
    teacher.save(update_fields=["project_status", "status_since"])

    handler.resolve_alerts(processed)
    assert (
        Alert.objects.filter(
            object_id=teacher.pk, alert_type=handler.alert_type, is_resolved=False
        ).count()
        == 0
    )
    assert processed["resolved"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_leave_creates_and_resolves(coordinator_on_leave: Coordinator) -> None:
    coord = coordinator_on_leave
    past = timezone.now() - timedelta(days=15)  # > 2 недель
    CoordinatorLogEvent.objects.create(
        coordinator=coord, type=CoordinatorLogEventType.GONE_ON_LEAVE, comment="", date_time=past
    )

    handler = CoordinatorOverdueLeaveHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=coord.pk, alert_type=handler.alert_type).first()
    assert alert is not None

    # coordinator вернулся -> статус меняем -> алерт резолвится
    coord.project_status = CoordinatorProjectStatus.WORKING_OK
    coord.save(update_fields=["project_status", "status_since"])
    handler.resolve_alerts(processed)
    alert.refresh_from_db()
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_leave_no_alert_for_recent_event(
    coordinator_on_leave: Coordinator,
) -> None:
    coord = coordinator_on_leave
    recent = timezone.now() - timedelta(days=1)
    CoordinatorLogEvent.objects.create(
        coordinator=coord, type=CoordinatorLogEventType.GONE_ON_LEAVE, comment="", date_time=recent
    )

    handler = CoordinatorOverdueLeaveHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=coord.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_leave_no_alert_for_non_leave_status(
    coordinator_on_leave: Coordinator,
) -> None:
    coord = coordinator_on_leave
    past = timezone.now() - timedelta(days=15)  # > 2 недель
    CoordinatorLogEvent.objects.create(
        coordinator=coord, type=CoordinatorLogEventType.GONE_ON_LEAVE, comment="", date_time=past
    )
    coord.project_status = CoordinatorProjectStatus.WORKING_OK
    coord.save(update_fields=["project_status", "status_since"])

    handler = CoordinatorOverdueLeaveHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=coord.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_utils_create_and_resolve(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    alert_type = "custom_test"

    alert = create_alert_for_object(teacher, alert_type, "detail")
    assert alert is not None
    # повторный вызов не должен создавать новый алерт
    alert_2 = create_alert_for_object(teacher, alert_type, "detail")
    assert alert_2 is not None
    assert alert_2.pk == alert.pk

    resolved = resolve_alerts_for_objects(Teacher, [teacher.pk], alert_type)
    assert resolved == 1
    alert.refresh_from_db()
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_celery_task_aggregates_counts(mocker: MockerFixture, teacher_no_group: Teacher) -> None:
    """check_system_alerts должен возвращать корректные счётчики."""
    # patch ALERT_HANDLERS для ускорения
    mocker.patch("alerts.handlers.ALERT_HANDLERS", [TeacherNoGroup45DaysHandler])

    past = timezone.now() - timedelta(days=46)
    TeacherLogEvent.objects.create(
        teacher=teacher_no_group,
        type=TeacherLogEventType.AWAITING_OFFER,
        comment="",
        date_time=past,
    )

    result = check_system_alerts()
    assert "Created: 1" in result
