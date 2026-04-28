from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_number', 'service_title', 'organization', 'client', 'status')
    list_filter = ('organization', 'status')
