from django.urls import path, include
from .views import ChangeClientStatusView, ClientCreateView, ClientListView

urlpatterns = [
    path('', ClientListView.as_view(), name='client_list'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('change-status/<int:pk>/', ChangeClientStatusView.as_view(), name='change_client_status'),
]