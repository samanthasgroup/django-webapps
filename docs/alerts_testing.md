# Alerts: local testing scenario

This doc describes a repeatable manual scenario for local alert checks and ideas for automation.

## Manual scenario (coordinator overdue leave)

Prereqs:
- DB is up, migrations applied, and you have a coordinator ID to test with.
- Admin or shell access to update coordinator status.

Steps:
1) Set coordinator `project_status` to `on_leave`.
   - Admin UI: open the coordinator and set Project status to "On leave".
   - Or via shell:
     ```bash
     uv run manage.py shell -c "from api.models import Coordinator; c=Coordinator.objects.get(pk=<CID>); c.project_status='on_leave'; c.save(update_fields=['project_status'])"
     ```
2) Create a log event in the past (e.g. 3 weeks ago):
   ```bash
   uv run manage.py create_coordinator_log <CID> gone_on_leave --ago "3 weeks" --comment "Test overdue leave"
   ```
3) Run the alert check task (sync):
   ```bash
   uv run manage.py trigger_task alerts.tasks.check_system_alerts --sync
   ```
4) Verify the alert:
   - Admin: Coordinator change page → Alerts inline.
   - Or Admin: Alerts list page filtered by `alert_type=overdue_on_leave` and `is_resolved=false`.

Resolution check:
1) Change coordinator `project_status` to a non-leave value (e.g. `working_ok`).
2) Re-run:
   ```bash
   uv run manage.py trigger_task alerts.tasks.check_system_alerts --sync
   ```
3) The alert should be marked resolved.

Notes:
- The `create_coordinator_log` command only creates a log event, it does not change `project_status`.
- If you already have an active alert for this coordinator, no duplicate will be created.

## Quick manual sanity (alert without conditions)

To verify alert wiring without status logic:
```bash
uv run manage.py create_alert api.Coordinator <CID> overdue_on_leave --details "Manual test"
```

## Automation ideas

Yes, this can be automated. Two practical options:

1) Pytest unit/integration tests
   - There is already coverage under `alerts/tests/test_alerts_module.py`.
   - Add tests that:
     - Create a coordinator with `project_status='on_leave'`.
     - Create a `CoordinatorLogEvent` with `date_time` older than 14 days.
     - Run `CoordinatorOverdueLeaveHandler().check_and_create_alerts(...)`.
     - Assert that an `Alert` exists.
     - Flip `project_status` and call `resolve_alerts` to assert it resolves.
   - This avoids Celery/Beat and runs fast in CI.

2) Management command + task runner
   - Add a small script/Make target that:
     - Creates seed data.
     - Runs `trigger_task alerts.tasks.check_system_alerts --sync`.
     - Prints alert counts.
   - This is closer to end-to-end but depends on DB state.

If you want, I can add the pytest coverage and a convenience make target.
