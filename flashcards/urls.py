from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import generate_ai_images

urlpatterns = [
	path('', views.home, name='home'),
	path('deck/', views.deck, name='deck'),
	path('deck/<str:deck_name>', views.deck, name='deck'),
	path('card/<str:deck_name>/<str:word>', views.card, name='card'),
	path('card/<str:deck_name>', views.card, name='card'),
 	path('mycards/', views.my_cards, name='my_cards'),  # Updated URL pattern
    path('mydecks/', views.my_decks, name='my_decks'),  # Updated URL pattern
    path('mydecks/<str:deck_name>', views.my_decks, name='my_decks'),
 	path('update_primary_image/', views.update_primary_image, name='update_primary_image'),
	path('log_correct_click', views.log_correct_click, name='log_correct_click'),
	path('generate_ai_images/', generate_ai_images, name='generate_ai_images'),
	path('generate_bulk_ai_images/', views.generate_bulk_ai_images, name='generate_bulk_ai_images'),
    #path('task-status/<str:task_id>/', views.get_task_status, name='task_status'),
]
