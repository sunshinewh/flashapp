from django.shortcuts import render
from django.contrib import messages
#from .models import EditPhoto
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
#from .tasks import convert_to_sketch


