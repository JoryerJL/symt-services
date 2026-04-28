from django.test import TestCase

from organization.models import Organization

from .models import Address, Client
from .selectors import get_client_by_id, get_clients_for_org
from .services import address_create, client_create, client_toggle_status


class ClientOrganizationTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")

    def test_client_has_organization_field(self):
        field = Client._meta.get_field('organization')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)
        self.assertEqual(field.related_model, Organization)

    def test_client_can_belong_to_organization(self):
        client = Client.objects.create(first_name="Maria", organization=self.org)
        self.assertEqual(client.organization, self.org)

    def test_filter_clients_by_organization(self):
        org_b = Organization.objects.create(name="Org B", slug="org-b")
        Client.objects.create(first_name="A", organization=self.org)
        Client.objects.create(first_name="B", organization=org_b)
        result = Client.objects.filter(organization=self.org)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().first_name, "A")


class ClientSelectorsTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")
        self.client_obj = Client.objects.create(first_name="Juan", organization=self.org, is_active=True)
        self.inactive = Client.objects.create(first_name="Pedro", organization=self.org, is_active=False)
        self.other_org = Client.objects.create(first_name="Maria", organization=self.org_b)

    def test_get_clients_for_org_returns_only_active_in_org(self):
        qs = get_clients_for_org(org=self.org)
        self.assertIn(self.client_obj, qs)
        self.assertNotIn(self.inactive, qs)
        self.assertNotIn(self.other_org, qs)

    def test_get_client_by_id_returns_correct(self):
        result = get_client_by_id(org=self.org, client_id=self.client_obj.pk)
        self.assertEqual(result, self.client_obj)

    def test_get_client_by_id_raises_if_wrong_org(self):
        with self.assertRaises(Exception):
            get_client_by_id(org=self.org, client_id=self.other_org.pk)


class ClientServicesTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.client_obj = Client.objects.create(first_name="Juan", organization=self.org, is_active=True)

    def test_address_create_persists_address(self):
        result = address_create(
            street="Calle 1",
            number="123",
            colony="Centro",
            city="CDMX",
            state="CDMX",
            country="Mexico",
            postal_code="01000",
        )
        self.assertIsInstance(result, Address)
        self.assertEqual(result.street, "Calle 1")
        self.assertEqual(Address.objects.count(), 1)

    def test_client_create_assigns_organization(self):
        result = client_create(org=self.org, first_name="Nuevo Cliente")
        self.assertEqual(result.organization, self.org)
        self.assertEqual(result.first_name, "Nuevo Cliente")

    def test_client_toggle_status_deactivates_active_client(self):
        result = client_toggle_status(client=self.client_obj)
        self.assertFalse(result.is_active)
        self.client_obj.refresh_from_db()
        self.assertFalse(self.client_obj.is_active)

    def test_client_toggle_status_reactivates_inactive_client(self):
        self.client_obj.is_active = False
        self.client_obj.save()
        result = client_toggle_status(client=self.client_obj)
        self.assertTrue(result.is_active)
        self.client_obj.refresh_from_db()
        self.assertTrue(self.client_obj.is_active)
