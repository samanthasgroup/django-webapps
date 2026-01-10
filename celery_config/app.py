import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")

app = Celery("django_webapps")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["celery_config", "alerts"])

app.conf.beat_schedule = {
    "check-system-alerts-hourly": {
        "task": "alerts.tasks.check_system_alerts",
        "schedule": crontab(minute=0),
    },
    # ...
}
