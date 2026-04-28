from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'company', 'phone_number', 'organization', 'is_active')
    list_filter = ('organization', 'is_active')
