from django.db.models import QuerySet

from organization.models import Organization

from .models import Client


def get_clients_for_org(*, org: Organization) -> QuerySet:
    return Client.objects.filter(organization=org, is_active=True)


def get_client_by_id(*, org: Organization, client_id: int) -> Client:
    return Client.objects.get(organization=org, pk=client_id)
