import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_webapps.settings")

app = Celery("django_webapps")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["celery_config"])
