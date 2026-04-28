from django.db import transaction
from django.test import TestCase

from client.models import Client
from organization.models import Organization

from .models import Service


class ServiceOrganizationTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")
        self.client_obj = Client.objects.create(first_name="Cliente Test", organization=self.org)

    def test_service_has_organization_field(self):
        field = Service._meta.get_field('organization')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)
        self.assertEqual(field.related_model, Organization)

    def test_service_can_belong_to_organization(self):
        svc = Service.objects.create(
            organization=self.org, client=self.client_obj, service_title="Svc 1"
        )
        self.assertEqual(svc.organization, self.org)

    def test_filter_services_by_organization(self):
        org_b = Organization.objects.create(name="Org B", slug="org-b")
        client_b = Client.objects.create(first_name="Cliente B", organization=org_b)
        Service.objects.create(organization=self.org, client=self.client_obj, service_title="Svc A")
        Service.objects.create(organization=org_b, client=client_b, service_title="Svc B")
        result = Service.objects.filter(organization=self.org)
        self.assertEqual(result.count(), 1)

    def test_service_number_unique_per_org(self):
        Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="S1", service_number=1
        )
        with self.assertRaises(Exception):
            with transaction.atomic():
                Service.objects.create(
                    organization=self.org, client=self.client_obj,
                    service_title="S2", service_number=1
                )

    def test_same_service_number_allowed_in_different_orgs(self):
        org_b = Organization.objects.create(name="Org B", slug="org-b")
        client_b = Client.objects.create(first_name="Cliente B", organization=org_b)
        Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="S1", service_number=1
        )
        svc_b = Service.objects.create(
            organization=org_b, client=client_b,
            service_title="S2", service_number=1
        )
        self.assertIsNotNone(svc_b.pk)
