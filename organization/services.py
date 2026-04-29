from django.contrib.auth.models import User
from django.db import transaction
from django.utils.text import slugify

from .models import Organization, UserProfile


@transaction.atomic
def organization_create(*, name: str) -> Organization:
    base_slug = slugify(name)
    slug = base_slug
    suffix = 1

    while Organization.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1

    organization = Organization(name=name, slug=slug)
    organization.full_clean()
    organization.save()
    return organization


@transaction.atomic
def organization_update_name(*, organization: Organization, name: str) -> Organization:
    organization.name = name
    organization.full_clean()
    organization.save(update_fields=['name', 'updated_at'])
    return organization


@transaction.atomic
def organization_toggle_active(*, organization: Organization) -> Organization:
    organization.is_active = not organization.is_active
    organization.save(update_fields=['is_active', 'updated_at'])
    return organization


@transaction.atomic
def organization_assign_user(*, organization: Organization, user: User) -> UserProfile:
    if hasattr(user, 'profile'):
        raise ValueError('El usuario ya tiene una organización asignada.')

    return UserProfile.objects.create(user=user, organization=organization)
