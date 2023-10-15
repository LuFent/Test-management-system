import os

from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_management_system.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")


app = Celery(
    "test_management_system",
)

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
