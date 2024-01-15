from celery import shared_task
from .models import EditPhoto
from django.conf import settings
from django.contrib.auth import get_user_model
from sketchify import sketch
import os
import time


