# App for creating and resolving alerts

## How to Add a New Alert Type

To add a new alert type in the future (for example, for students):

1. Add the new type to `AlertConfig.TYPES` in `config.py`
2. Create a new handler class in the corresponding file (e.g., `student.py`)
3. Register the handler in the `ALERT_HANDLERS` list in `handlers/__init__.py`

That's it! Your `check_system_alerts` task will automatically start using the new handler.

## Command for creation of new alerts

You can use the `create_alert` command to create new alerts for testing purposes.

```bash
uv run manage.py create_alert api.Coordinator 32 overdue_on_leave --details "Проверить статус отпуска вручную"
```

## Command for creation of log events

```bash
uv run manage.py create_coordinator_log 32 gone_on_leave --ago "3 weeks" --comment "Тестовое событие для проверки алерта"
```

## Command for triggering a task

```bash
python manage.py trigger_task <task_full_name> [--args '[arg1, arg2]'] [--kwargs '{"key": "value"}'] [--sync]
```

example:

```bash
uv run manage.py trigger_task alerts.tasks.check_system_alerts
```

or

```bash
uv run manage.py trigger_task alerts.tasks.check_system_alerts --sync
```
