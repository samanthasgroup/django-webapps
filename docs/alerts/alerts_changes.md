# Alert changes history

This document tracks recent alert-related changes and additions.

## 2025-01-06

Changes:
- Added new alert types:
  - `overdue_transfer_request` (coordinator transfer request older than 14 days)
  - `coordinator_onboarding_stale` (coordinator onboarding older than 14 days)
- Added new handlers:
  - `CoordinatorOverdueTransferRequestHandler`
  - `CoordinatorOnboardingStaleHandler`
- Added admin UI behavior:
  - Highlight coordinator rows with `situational_status=STALE`
  - Added filter "Onboarding stale"
- Added situational status:
  - `CoordinatorSituationalStatus.ONBOARDING`
- Added tests for:
  - overdue transfer request alert (create/no-create/resolve)
  - onboarding stale status update and alert

Files touched:
- `alerts/config.py`
- `alerts/handlers/coordinator.py`
- `alerts/handlers/__init__.py`
- `api/models/choices/status/situational.py`
- `api/admin/coordinator.py`
- `static/js/admin-coordinator-stale.js`
- `static/css/admin-coordinator-stale.css`
- `alerts/tests/test_alerts_module.py`
