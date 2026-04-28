from django.urls import path, include
from .views import EmployeeListView, EmployeeCreateView, change_employee_status

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('change-status/<int:pk>/', change_employee_status, name='change_employee_status'),
]