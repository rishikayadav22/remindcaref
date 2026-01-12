import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_assistant.settings')
app = Celery('emotion_assistant')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
