import os

from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nav_django.settings-dev')
# app = Celery("nav_django.settings-dev")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'experiment.settings')
app = Celery('experiment')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["utils.data_generator"])
