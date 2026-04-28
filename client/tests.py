from django.test import TestCase

from organization.models import Organization

from .models import Client


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
