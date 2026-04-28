from django.urls import path, include
from .views import ChangeEmployeeStatusView, EmployeeCreateView, EmployeeListView

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('change-status/<int:pk>/', ChangeEmployeeStatusView.as_view(), name='change_employee_status'),
]