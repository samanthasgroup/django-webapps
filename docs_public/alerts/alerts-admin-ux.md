# Admin Alerts UX Improvements

## What changed
- Alerts now have human-readable labels via model choices and badges.
- Alert details show a preview with a full-text tooltip.
- Resolving/unresolving alerts in admin keeps `resolved_at` consistent.
- Active alert counts are shown on coordinator/student/teacher/group lists.
- Rows with active alerts are highlighted on coordinator/student/teacher/group lists.
- Alert inlines are available on coordinator, student, teacher, and group pages.
- Alert list filters now include alert type and resolved status on all these admin pages.

## Where to review in admin
- Alerts list: `Admin -> Alerts -> Alerts`
  - Check type badges, details preview, and related object link.
- Coordinator list: `Admin -> Api -> Coordinators`
  - See the `Active Alerts` column and alert filters.
  - Rows with active alerts should be highlighted.
- Coordinator detail: `Admin -> Api -> Coordinators -> <coordinator>`
  - See the Alerts inline with type badges and details preview.
- Student list: `Admin -> Api -> Students`
  - See the `Active Alerts` column and alert filters.
  - Rows with active alerts should be highlighted.
- Student detail: `Admin -> Api -> Students -> <student>`
  - See the Alerts inline.
- Teacher list: `Admin -> Api -> Teachers`
  - See the `Active Alerts` column and alert filters.
  - Rows with active alerts should be highlighted.
- Teacher detail: `Admin -> Api -> Teachers -> <teacher>`
  - See the Alerts inline.
- Group list: `Admin -> Api -> Groups`
  - See the `Active Alerts` column and alert filters.
  - Rows with active alerts should be highlighted.
- Group detail: `Admin -> Api -> Groups -> <group>`
  - See the Alerts inline.

## Quick demo alerts
Create alerts without waiting for handlers:
```
uv run manage.py seed_demo_alerts --group-id <GID> --student-id <SID> --teacher-id <TID> --coordinator-id <CID>
```

Auto-pick the first available objects when you do not want to provide IDs:
```
uv run manage.py seed_demo_alerts --auto
```

Use Celery to enqueue alert creation (worker + broker must be running):
```
uv run manage.py seed_demo_alerts --group-id <GID> --use-celery
```

Auto-pick IDs and enqueue via Celery:
```
uv run manage.py seed_demo_alerts --auto --use-celery
```

Run the Celery task synchronously (without a worker):
```
uv run manage.py seed_demo_alerts --group-id <GID> --use-celery --sync
```
