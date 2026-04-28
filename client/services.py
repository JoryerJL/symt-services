from organization.models import Organization

from .models import Client


def client_create(
    *,
    org: Organization,
    first_name: str,
    company: str = None,
    phone_number: str = None,
    responsible: str = None,
    address=None,
) -> Client:
    client = Client(
        organization=org,
        first_name=first_name,
        company=company,
        phone_number=phone_number,
        responsible=responsible,
        address=address,
    )
    client.full_clean()
    client.save()
    return client


def client_toggle_status(*, client: Client) -> Client:
    client.is_active = not client.is_active
    client.save(update_fields=['is_active'])
    return client
