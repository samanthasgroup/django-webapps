from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from alerts.config import AlertConfig
from alerts.models import Alert
from alerts.tasks import create_demo_alerts
from api.models import Coordinator, Group, Student, Teacher


class Command(BaseCommand):
    help = "Create demo alerts for quick admin UI проверки."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--group-id", type=int, help="Group ID to create a demo alert for")
        parser.add_argument("--student-id", type=int, help="Student ID to create a demo alert for")
        parser.add_argument("--teacher-id", type=int, help="Teacher ID to create a demo alert for")
        parser.add_argument("--coordinator-id", type=int, help="Coordinator ID to create a demo alert for")
        parser.add_argument(
            "--auto",
            action="store_true",
            help="Pick the first available group/student/teacher/coordinator if no IDs are provided",
        )
        parser.add_argument(
            "--use-celery",
            action="store_true",
            help="Enqueue creation via Celery (requires running worker and broker)",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run the Celery task synchronously (useful without a worker)",
        )

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: ARG002
        group_id = options.get("group_id")
        student_id = options.get("student_id")
        teacher_id = options.get("teacher_id")
        coordinator_id = options.get("coordinator_id")
        auto = bool(options.get("auto"))
        use_celery = bool(options.get("use_celery"))
        sync = bool(options.get("sync"))

        if not any([group_id, student_id, teacher_id, coordinator_id]) and not auto:
            raise CommandError(
                "Provide at least one of --group-id/--student-id/--teacher-id/--coordinator-id or use --auto."
            )

        if auto:
            group_id = group_id or self._first_id(Group)
            student_id = student_id or self._first_id(Student)
            teacher_id = teacher_id or self._first_id(Teacher)
            coordinator_id = coordinator_id or self._first_id(Coordinator)
            self.stdout.write(
                "Auto-picked IDs -> "
                f"group:{group_id} student:{student_id} teacher:{teacher_id} coordinator:{coordinator_id}"
            )

        alert_specs: list[dict[str, str | int]] = []
        alert_specs.extend(self._build_specs(Group, group_id, AlertConfig.TYPES["GROUP_PENDING_OVERDUE"]))
        alert_specs.extend(self._build_specs(Student, student_id, AlertConfig.TYPES["STUDENT_NO_GROUP_30_DAYS"]))
        alert_specs.extend(self._build_specs(Teacher, teacher_id, AlertConfig.TYPES["TEACHER_NO_GROUP_45_DAYS"]))
        alert_specs.extend(self._build_specs(Coordinator, coordinator_id, AlertConfig.TYPES["OVERDUE_ON_LEAVE"]))

        if not alert_specs:
            raise CommandError("No valid objects found for the provided IDs.")

        if use_celery:
            if sync:
                created = create_demo_alerts(alert_specs)
                self.stdout.write(self.style.SUCCESS(f"Created {created} demo alert(s) via Celery (sync)."))
            else:
                async_result = create_demo_alerts.delay(alert_specs)
                self.stdout.write(self.style.SUCCESS(f"Enqueued demo alerts via Celery. Task id: {async_result.id}"))
            return

        with transaction.atomic():
            created = 0
            for spec in alert_specs:
                Alert.objects.create(
                    alert_type=str(spec["alert_type"]),
                    content_type_id=int(spec["content_type_id"]),
                    object_id=int(spec["object_id"]),
                    details=str(spec.get("details", "")),
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} demo alert(s)."))

    def _build_specs(self, model: type[Any], obj_id: int | None, alert_type: str) -> list[dict[str, str | int]]:
        if not obj_id:
            return []
        if not model.objects.filter(pk=obj_id).exists():
            raise CommandError(f"{model.__name__} with id={obj_id} does not exist.")
        content_type = ContentType.objects.get_for_model(model)
        return [
            {
                "alert_type": alert_type,
                "content_type_id": content_type.pk,
                "object_id": obj_id,
                "details": f"Demo alert for {model.__name__} #{obj_id}",
            }
        ]

    def _first_id(self, model: type[Any]) -> int | None:
        obj = model.objects.order_by("pk").first()
        return obj.pk if obj else None
