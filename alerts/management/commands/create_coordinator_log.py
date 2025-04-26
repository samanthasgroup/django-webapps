import re
from argparse import ArgumentParser
from datetime import timedelta
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from api.models.choices.log_event_type import CoordinatorLogEventType

try:
    Coordinator = apps.get_model("api", "Coordinator")
except LookupError:
    raise CommandError(
        "Could not find model 'coordinators.Coordinator'. Adjust the app_label in the command."
    )

try:
    CoordinatorLogEvent = apps.get_model("api", "CoordinatorLogEvent")
except LookupError:
    raise CommandError("Could not find models 'CoordinatorLogEvent' in 'api'")


class Command(BaseCommand):
    help = (
        "Creates a CoordinatorLogEvent for a given coordinator with a specified type "
        "and sets the date to a specified time in the past (e.g., '3 weeks ago'). "
        "Useful for testing alert conditions."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "coordinator_id", type=int, help="The primary key (ID) of the Coordinator."
        )
        parser.add_argument(
            "event_type",
            type=str,
            help=f"The event type string. Must be one of {list(CoordinatorLogEventType.values)}. "
            f'Example: "{CoordinatorLogEventType.GONE_ON_LEAVE.value}" for testing leave alerts.',
        )
        parser.add_argument(
            "--ago",
            type=str,
            required=True,
            help='Time duration in the past. Format: "number unit" (e.g., "3 weeks", "15 days", "2 hours"). '
            "Supported units: days, weeks, hours, minutes.",
        )
        parser.add_argument(
            "--comment",
            type=str,
            default="Log event created via management command.",
            help="Optional comment for the log event.",
        )

    def parse_ago_string(self, ago_str: str) -> timedelta:
        """Parses strings like '3 weeks', '15 days' into a timedelta."""
        match = re.match(r"(\d+)\s+(day|week|hour|minute)s?", ago_str, re.IGNORECASE)
        if not match:
            raise ValueError(
                "Invalid format for --ago. Use 'number unit' (e.g., '3 weeks', '15 days'). "
                "Supported units: days, weeks, hours, minutes."
            )

        value = int(match.group(1))
        unit = match.group(2).lower()

        seconds_per_unit: dict[str, int] = {
            "minute": 60,
            "hour": 3600,
            "day": 86400,
            "week": 604800,
        }
        singular_unit = unit.rstrip("s")

        try:
            total_seconds = seconds_per_unit[singular_unit] * value
        except KeyError:
            raise ValueError(
                f"Invalid unit '{unit}' for --ago. Supported units: days, weeks, hours, minutes."
            )

        return timedelta(seconds=total_seconds)

    def handle(self, **options: Any) -> None:
        coordinator_id = options["coordinator_id"]
        event_type_str = options["event_type"]
        ago_str = options["ago"]
        comment = options["comment"]

        # 1. Найти координатора
        try:
            coordinator = Coordinator.objects.get(pk=coordinator_id)
        except Coordinator.DoesNotExist:
            raise CommandError(f"Coordinator with ID {coordinator_id} not found.")

        # 2. Проверить тип события
        if event_type_str not in CoordinatorLogEventType.values:
            valid_types = ", ".join(CoordinatorLogEventType.values)
            raise CommandError(
                f"Invalid event_type {event_type_str}. Must be one of: {valid_types}"
            )
        # Получаем реальное значение Enum (если используется TextChoices/Enum)
        event_type = CoordinatorLogEventType(event_type_str)

        # 3. Рассчитать дату в прошлом
        try:
            time_delta = self.parse_ago_string(ago_str)
            event_datetime = timezone.now() - time_delta
        except ValueError as e:
            raise CommandError(f"Error parsing --ago value: {e}")

        # 4. Создать лог событие
        try:
            log_event = CoordinatorLogEvent.objects.create(
                coordinator=coordinator, type=event_type, date_time=event_datetime, comment=comment
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created CoordinatorLogEvent (ID: {log_event.pk}) "
                    f"for Coordinator '{coordinator}' (ID: {coordinator_id}) "
                    f"with type '{event_type}' and date_time set to {event_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}."
                )
            )
        except Exception as e:
            raise CommandError(f"Failed to create log event: {e}")
