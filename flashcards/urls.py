from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

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
]
