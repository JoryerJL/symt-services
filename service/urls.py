from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import ServiceListView, ServiceCreateView, AssignEmployeeView, reactivate_service, ServiceDetailView, generate_report_view, ServiceSummaryUpdateView

urlpatterns = [
    path('', login_required(ServiceListView.as_view()), name='services_list'),
    path('create/', login_required(ServiceCreateView.as_view()), name='services_create'),
    path('assign-employee/', login_required(AssignEmployeeView.as_view()), name='assign_employee'),
    path('reactivate-service/<int:pk>/', login_required(reactivate_service), name='reactivate_service'),
    path('<int:pk>/', login_required(ServiceDetailView.as_view()), name='service_detail'),
    path('<int:pk>/generate-report/', login_required(generate_report_view), name='generate_report'),
    path('update-summary/', login_required(ServiceSummaryUpdateView.as_view()), name='update_service_summary'),
]