from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker
from pytest_mock import MockerFixture

from alerts.handlers.coordinator import (
    CoordinatorOnboardingStaleHandler,
    CoordinatorOverdueLeaveHandler,
    CoordinatorOverdueTransferRequestHandler,
)
from alerts.handlers.group import GroupAwaitingStartOverdueHandler, GroupPendingOverdueHandler
from alerts.handlers.student import (
    StudentNeedsOralInterviewHandler,
    StudentNoGroup30DaysHandler,
    StudentOverdueGroupOfferHandler,
)
from alerts.handlers.teacher import (
    TeacherNoGroup45DaysHandler,
    TeacherOverdueGroupOfferHandler,
    TeacherOverdueOnLeaveHandler,
)
from alerts.models import Alert
from alerts.tasks import check_system_alerts
from alerts.utils import create_alert_for_object, resolve_alerts_for_objects
from api.models.choices.log_event_type import CoordinatorLogEventType, StudentLogEventType, TeacherLogEventType
from api.models.choices.registration_telegram_bot_language import RegistrationTelegramBotLanguage
from api.models.choices.status import GroupProjectStatus, StudentProjectStatus, TeacherProjectStatus
from api.models.choices.status.project import CoordinatorProjectStatus
from api.models.choices.status.situational import CoordinatorSituationalStatus
from api.models.coordinator import Coordinator
from api.models.group import Group
from api.models.log_event import CoordinatorLogEvent, StudentLogEvent, TeacherLogEvent
from api.models.personal_info import PersonalInfo
from api.models.student import Student
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


@pytest.fixture  # type: ignore[misc]
def student_no_group(personal_info: PersonalInfo) -> Student:
    """Ученик со статусом NO_GROUP_YET."""
    return baker.make(
        Student,
        personal_info=personal_info,
        project_status=StudentProjectStatus.NO_GROUP_YET,
        status_since=timezone.now(),
        _fill_optional=True,
        make_m2m=True,
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
    TeacherLogEvent.objects.create(teacher=teacher, type=TeacherLogEventType.AWAITING_OFFER, comment="", date_time=past)

    handler = TeacherNoGroup45DaysHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    # меняем статус -> алерт должен резолвиться
    teacher.project_status = TeacherProjectStatus.WORKING
    teacher.save(update_fields=["project_status", "status_since"])

    handler.resolve_alerts(processed)
    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type, is_resolved=False).count() == 0
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
def test_student_oral_interview_overdue_creates_and_resolves(student_no_group: Student) -> None:
    student = student_no_group
    student.project_status = StudentProjectStatus.NEEDS_INTERVIEW_TO_DETERMINE_LEVEL
    student.status_since = timezone.now() - timedelta(days=15)
    student.save(update_fields=["project_status", "status_since"])

    handler = StudentNeedsOralInterviewHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=student.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1

    student.project_status = StudentProjectStatus.NO_GROUP_YET
    student.save(update_fields=["project_status", "status_since"])
    handler.resolve_alerts(processed)

    alert.refresh_from_db()
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_student_overdue_group_offer_creates_alert(student_no_group: Student) -> None:
    student = student_no_group
    past = timezone.now() - timedelta(days=15)
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.GROUP_OFFERED,
        comment="",
        date_time=past,
    )

    handler = StudentOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=student.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_student_overdue_group_offer_no_alert_after_response(student_no_group: Student) -> None:
    student = student_no_group
    past = timezone.now() - timedelta(days=15)
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.GROUP_OFFERED,
        comment="",
        date_time=past,
    )
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.ACCEPTED_OFFER,
        comment="",
        date_time=past + timedelta(days=1),
    )

    handler = StudentOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=student.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_student_overdue_group_offer_no_alert_if_recent_offer_exists(student_no_group: Student) -> None:
    student = student_no_group
    old_offer = timezone.now() - timedelta(days=20)
    recent_offer = timezone.now() - timedelta(days=2)
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.GROUP_OFFERED,
        comment="",
        date_time=old_offer,
    )
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.GROUP_OFFERED,
        comment="",
        date_time=recent_offer,
    )

    handler = StudentOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=student.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_student_no_group_30_days_creates_alert(student_no_group: Student) -> None:
    student = student_no_group
    past = timezone.now() - timedelta(days=31)
    StudentLogEvent.objects.create(
        student=student,
        type=StudentLogEventType.AWAITING_OFFER,
        comment="",
        date_time=past,
    )

    handler = StudentNoGroup30DaysHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=student.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_group_pending_overdue_creates_and_resolves() -> None:
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        project_status=GroupProjectStatus.PENDING,
        status_since=timezone.now() - timedelta(days=15),
    )

    handler = GroupPendingOverdueHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=group.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1

    group.project_status = GroupProjectStatus.AWAITING_START
    group.save(update_fields=["project_status", "status_since"])
    handler.resolve_alerts(processed)

    alert.refresh_from_db()
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_group_awaiting_start_overdue_creates_alert() -> None:
    group = baker.make(
        Group,
        _fill_optional=True,
        make_m2m=True,
        project_status=GroupProjectStatus.AWAITING_START,
        status_since=timezone.now() - timedelta(days=15),
    )

    handler = GroupAwaitingStartOverdueHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=group.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_leave_creates_and_resolves(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    teacher.project_status = TeacherProjectStatus.ON_LEAVE
    teacher.save(update_fields=["project_status", "status_since"])
    past = timezone.now() - timedelta(days=15)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GONE_ON_LEAVE,
        comment="",
        date_time=past,
    )

    handler = TeacherOverdueOnLeaveHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1

    teacher.project_status = TeacherProjectStatus.WORKING
    teacher.save(update_fields=["project_status", "status_since"])
    handler.resolve_alerts(processed)
    alert.refresh_from_db()
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_group_offer_creates_alert(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    past = timezone.now() - timedelta(days=15)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=past,
    )

    handler = TeacherOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_group_offer_no_alert_for_recent_event(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=timezone.now(),
    )

    handler = TeacherOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_group_offer_no_alert_after_response(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    past = timezone.now() - timedelta(days=15)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=past,
    )
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.DECLINED_OFFER,
        comment="",
        date_time=past + timedelta(days=1),
    )

    handler = TeacherOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_group_offer_no_alert_if_recent_offer_exists(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    old_offer = timezone.now() - timedelta(days=20)
    recent_offer = timezone.now() - timedelta(days=2)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=old_offer,
    )
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=recent_offer,
    )

    handler = TeacherOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_teacher_overdue_group_offer_resolves_after_status_change(teacher_no_group: Teacher) -> None:
    teacher = teacher_no_group
    past = timezone.now() - timedelta(days=15)
    TeacherLogEvent.objects.create(
        teacher=teacher,
        type=TeacherLogEventType.GROUP_OFFERED,
        comment="",
        date_time=past,
    )

    handler = TeacherOverdueGroupOfferHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    teacher.project_status = TeacherProjectStatus.WORKING
    teacher.save(update_fields=["project_status", "status_since"])
    handler.resolve_alerts(processed)

    assert Alert.objects.filter(object_id=teacher.pk, alert_type=handler.alert_type, is_resolved=False).count() == 0
    assert processed["resolved"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_transfer_request_creates_alert() -> None:
    coordinator = baker.make(Coordinator, _fill_optional=True)
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    past = timezone.now() - timedelta(days=15)
    CoordinatorLogEvent.objects.create(
        coordinator=coordinator,
        group=group,
        type=CoordinatorLogEventType.REQUESTED_TRANSFER,
        comment="",
        date_time=past,
    )

    handler = CoordinatorOverdueTransferRequestHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    alert = Alert.objects.filter(object_id=coordinator.pk, alert_type=handler.alert_type, is_resolved=False).first()
    assert alert is not None
    assert processed["created"] == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_transfer_request_recent_no_alert() -> None:
    coordinator = baker.make(Coordinator, _fill_optional=True)
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    CoordinatorLogEvent.objects.create(
        coordinator=coordinator,
        group=group,
        type=CoordinatorLogEventType.REQUESTED_TRANSFER,
        comment="",
        date_time=timezone.now(),
    )

    handler = CoordinatorOverdueTransferRequestHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    assert Alert.objects.filter(object_id=coordinator.pk, alert_type=handler.alert_type).count() == 0
    assert processed["created"] == 0


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_overdue_transfer_request_resolves_after_cancel() -> None:
    coordinator = baker.make(Coordinator, _fill_optional=True)
    group = baker.make(Group, _fill_optional=True, make_m2m=True)
    past = timezone.now() - timedelta(days=15)
    CoordinatorLogEvent.objects.create(
        coordinator=coordinator,
        group=group,
        type=CoordinatorLogEventType.REQUESTED_TRANSFER,
        comment="",
        date_time=past,
    )

    handler = CoordinatorOverdueTransferRequestHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    cancel_time = past + timedelta(days=1)
    CoordinatorLogEvent.objects.create(
        coordinator=coordinator,
        group=group,
        type=CoordinatorLogEventType.TRANSFER_CANCELED,
        comment="",
        date_time=cancel_time,
    )
    handler.resolve_alerts(processed)

    alert = Alert.objects.filter(object_id=coordinator.pk, alert_type=handler.alert_type).first()
    assert alert is not None
    assert alert.is_resolved


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_onboarding_stale_updates_status_and_creates_alert() -> None:
    coordinator = baker.make(
        Coordinator,
        _fill_optional=True,
        situational_status=CoordinatorSituationalStatus.ONBOARDING,
        status_since=timezone.now() - timedelta(days=15),
    )

    handler = CoordinatorOnboardingStaleHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    coordinator.refresh_from_db()
    assert coordinator.situational_status == CoordinatorSituationalStatus.STALE
    assert Alert.objects.filter(object_id=coordinator.pk, alert_type=handler.alert_type).count() == 1


@pytest.mark.django_db  # type: ignore[misc]
def test_coordinator_onboarding_stale_recent_no_alert() -> None:
    coordinator = baker.make(
        Coordinator,
        _fill_optional=True,
        situational_status=CoordinatorSituationalStatus.ONBOARDING,
        status_since=timezone.now(),
    )

    handler = CoordinatorOnboardingStaleHandler()
    processed = {"created": 0, "resolved": 0}
    handler.check_and_create_alerts(processed)

    coordinator.refresh_from_db()
    assert coordinator.situational_status == CoordinatorSituationalStatus.ONBOARDING
    assert Alert.objects.filter(object_id=coordinator.pk, alert_type=handler.alert_type).count() == 0


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
    assert alert.resolved_at is not None


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
