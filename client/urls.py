from django.urls import path, include
from .views import ClientListView, ClientCreateView, change_client_status

urlpatterns = [
    path('', ClientListView.as_view(), name='client_list'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('change-status/<int:pk>/', change_client_status, name='change_client_status'),
]