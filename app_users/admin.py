from django.contrib import admin
from .models import AppUser  # Adjust the import according to your app structure

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'country')  # Add other fields as needed
    search_fields = ('email', 'username')
    # Add other admin options as needed


