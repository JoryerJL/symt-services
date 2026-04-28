from django.db.models import QuerySet

from organization.models import Organization

from .models import Service


def get_services_for_org(*, org: Organization) -> QuerySet:
    return Service.objects.filter(organization=org).order_by('-created_at')


def get_service_by_id(*, org: Organization, service_id: int) -> Service:
    return Service.objects.get(organization=org, pk=service_id)


def get_active_services(*, org: Organization) -> QuerySet:
    return get_services_for_org(org=org).exclude(status=Service.Status.Cancelled)


def get_services_by_status(*, org: Organization, status: int) -> QuerySet:
    return get_services_for_org(org=org).filter(status=status)
