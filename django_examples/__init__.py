from .celery import app as celery_app
from django.conf import settings

__all__ = ('celery_app',)
