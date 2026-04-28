from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'organization', 'is_active')
    list_filter = ('organization', 'is_active')
