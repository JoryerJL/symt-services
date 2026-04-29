from django.urls import path

from .views import (
    OrganizationAssignUserView,
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationToggleView,
    OrganizationUpdateView,
)

urlpatterns = [
    path('', OrganizationListView.as_view(), name='organization_list'),
    path('create/', OrganizationCreateView.as_view(), name='organization_create'),
    path('<slug:slug>/edit/', OrganizationUpdateView.as_view(), name='organization_edit'),
    path('<slug:slug>/', OrganizationDetailView.as_view(), name='organization_detail'),
    path('<slug:slug>/toggle/', OrganizationToggleView.as_view(), name='organization_toggle'),
    path('<slug:slug>/assign-user/', OrganizationAssignUserView.as_view(), name='organization_assign_user'),
]
