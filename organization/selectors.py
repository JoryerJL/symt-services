from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from .models import Organization, UserProfile
from service.models import Service


ACTIVE_ASSIGNED_STATUSES = [
    Service.Status.Active,
    Service.Status.Assigned,
    Service.Status.Reassigned,
]


def get_organizations_with_summary():
    return Organization.objects.annotate(
        members_count=Count('members', distinct=True),
        employees_count=Count('employees', distinct=True),
        clients_count=Count('clients', distinct=True),
        services_count=Count('services', distinct=True),
    ).order_by('name')


def get_organization_by_slug(*, slug: str) -> Organization:
    return get_object_or_404(Organization, slug=slug)


def get_organization_members(*, organization: Organization):
    return UserProfile.objects.filter(organization=organization).select_related('user').order_by('user__username')


def get_organization_stats(*, organization: Organization) -> dict:
    services = organization.services.all()
    return {
        'total_services': services.count(),
        'active_assigned_services': services.filter(status__in=ACTIVE_ASSIGNED_STATUSES).count(),
        'finished_services': services.filter(status=Service.Status.Cancelled).count(),
        'employees_count': organization.employees.count(),
        'clients_count': organization.clients.count(),
    }


def get_unassigned_users():
    return User.objects.filter(profile__isnull=True).order_by('username')
