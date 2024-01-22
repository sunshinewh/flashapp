from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Setting the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_examples.settings')

# Name your Celery app. It's common to name it after your Django project.
app = Celery('django_examples')

# Using Redis as broker, the configuration is taken from your Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

