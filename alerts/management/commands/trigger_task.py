import json
from argparse import ArgumentParser
from typing import Any

from celery import current_app
from celery.exceptions import TaskError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Triggers a Celery task by its registered name. "
        "Example: python manage.py trigger_task alerts.tasks.check_system_alerts"
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "task_name",
            type=str,
            help='The full registered name of the Celery task (e.g., "app_name.tasks.my_task").',
        )
        parser.add_argument(
            "--args",
            type=str,
            default="[]",
            help="JSON encoded list of positional arguments for the task (e.g., '[1, \"hello\"]').",
        )
        parser.add_argument(
            "--kwargs",
            type=str,
            default="{}",
            help='JSON encoded dictionary of keyword arguments for the task (e.g., \'{"user_id": 5, "force": true}\').',
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run the task synchronously in the current process (for debugging, ignores Celery worker).",
        )

    def handle(self, **options: Any) -> None:
        task_name = options["task_name"]
        args_json = options.get("args", "[]")
        kwargs_json = options.get("kwargs", "{}")
        run_sync = options["sync"]

        # 1. Парсинг аргументов JSON
        try:
            task_args = json.loads(args_json)
            if not isinstance(task_args, list):
                raise ValueError("Value for --args must be a JSON list.")
        except json.JSONDecodeError:
            raise CommandError(f"Invalid JSON format for --args: {args_json}")
        except ValueError as e:
            raise CommandError(str(e))

        try:
            task_kwargs = json.loads(kwargs_json)
            if not isinstance(task_kwargs, dict):
                raise ValueError("Value for --kwargs must be a JSON dictionary.")
        except json.JSONDecodeError:
            raise CommandError(f"Invalid JSON format for --kwargs: {kwargs_json}")
        except ValueError as e:
            raise CommandError(str(e))

        # 2. Проверка существования задачи (частичная, для sync)
        if run_sync:
            if task_name not in current_app.tasks:
                raise CommandError(
                    f"Task '{task_name}' not found in the current Celery app instance."
                )
            self.stdout.write(self.style.WARNING(f"Running task '{task_name}' synchronously..."))
            try:
                # Выполняем задачу напрямую
                result = current_app.tasks[task_name](*task_args, **task_kwargs)
                self.stdout.write(
                    self.style.SUCCESS(f"Task '{task_name}' finished synchronously.")
                )
                self.stdout.write(f"Result: {result}")  # Выводим результат, если он есть
            except Exception as e:
                raise CommandError(
                    f"Task '{task_name}' raised an exception during synchronous execution: {e}"
                )
        else:
            # 3. Отправка задачи в очередь через Celery
            self.stdout.write(f"Attempting to send task '{task_name}' to the queue...")
            try:
                # Используем send_task для отправки по имени
                async_result = current_app.send_task(
                    name=task_name, args=task_args, kwargs=task_kwargs
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Task '{task_name}' sent to the queue successfully.")
                )
                self.stdout.write(f"Task ID: {async_result.id}")
                self.stdout.write(
                    "Note: This only means the task was accepted by the broker. Check worker logs for execution."
                )
            except TaskError as e:
                raise CommandError(f"Task related error name: '{task_name}'. Error: {e}")
            except Exception as e:
                # Обработка других ошибок, например, проблем с подключением к брокеру
                raise CommandError(f"Failed to send task '{task_name}': {e}")
