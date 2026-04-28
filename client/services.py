from organization.models import Organization

from .models import Address, Client


def address_create(
    *,
    street: str,
    number: str,
    colony: str,
    city: str,
    state: str,
    country: str,
    postal_code: str,
) -> Address:
    address = Address(
        street=street,
        number=number,
        colony=colony,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code,
    )
    address.full_clean()
    address.save()
    return address


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
