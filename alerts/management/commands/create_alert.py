from argparse import ArgumentParser
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Model

from alerts.models import Alert


class Command(BaseCommand):
    help = (
        "Creates a new Alert for a specific model instance. "
        "Prevents creation if an identical active alert already exists."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "model_spec",
            type=str,
            help=(
                'Specification of the target model in format "app_label.ModelName" '
                '(e.g., "coordinators.Coordinator").'
            ),
        )
        parser.add_argument(
            "object_id",
            type=int,
            help="The primary key (ID) of the object instance to create the alert for.",
        )
        parser.add_argument(
            "alert_type",
            type=str,
            help='A string identifier for the type of alert (e.g., "overdue_on_leave", "manual_check_required").',
        )
        parser.add_argument(
            "--details", type=str, default="", help="Optional descriptive text for the alert."
        )

    def handle(self, **options: Any) -> None:
        model_spec = options["model_spec"]
        object_id = options["object_id"]
        alert_type = options["alert_type"]
        details = options["details"]

        # 1. Найти ContentType по строке 'app_label.ModelName'
        try:
            app_label, model_name = model_spec.split(".")
        except ValueError:
            raise CommandError(
                f"Invalid model_spec format: '{model_spec}'. Use 'app_label.ModelName'."
            )

        try:
            # Ищем модель без учета регистра, как это делает ContentType
            content_type = ContentType.objects.get(
                app_label=app_label.lower(), model=model_name.lower()
            )
            target_model = content_type.model_class()
            if target_model is None:
                # Это может случиться, если модель была удалена после создания ContentType
                raise CommandError(
                    f"Model class not found for {content_type}. The app '{app_label}' "
                    f"might be missing or the model removed."
                )
            assert issubclass(target_model, Model), f"{target_model} is not a Django model"
        except ContentType.DoesNotExist:
            raise CommandError(
                f"Model not found for spec '{model_spec}'. Check app_label and ModelName."
            )

        # 2. Найти целевой объект по ID
        try:
            from django.db.models import Manager

            if not hasattr(target_model, "objects") or not isinstance(
                target_model.objects, Manager
            ):
                raise CommandError(
                    f"{target_model.__name__} does not have a valid objects manager."
                )
            manager = getattr(target_model, "objects", None)
            if manager is None or not isinstance(manager, Manager):
                raise CommandError(
                    f"{target_model.__name__} does not have a valid objects manager."
                )
            target_object = manager.get(pk=object_id)
        except Exception as e:
            if isinstance(e, ValueError):
                raise CommandError(
                    f"Invalid ID format: '{object_id}' for model {target_model.__name__}."
                )
            raise CommandError(f"{target_model.__name__} with ID {object_id} not found: {e}")

        # 3. Проверить, существует ли уже идентичный активный алерт
        existing_alert = Alert.objects.filter(
            content_type=content_type,
            object_id=object_id,
            alert_type=alert_type,
            is_resolved=False,
        ).first()

        if existing_alert:
            self.stdout.write(
                self.style.WARNING(
                    f"An identical active alert (ID: {existing_alert.pk}) already exists for "
                    f"{target_model.__name__} ID {object_id} with type '{alert_type}'. Skipping creation."
                )
            )
            return

        # 4. Создать новый Alert
        try:
            new_alert = Alert.objects.create(
                content_type=content_type,
                object_id=object_id,
                alert_type=alert_type,
                details=details,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created Alert (ID: {new_alert.pk}) of type '{alert_type}' for "
                    f"{target_model.__name__} '{target_object}' (ID: {object_id})."
                )
            )
        except Exception as e:
            raise CommandError(f"Failed to create alert: {e}")
