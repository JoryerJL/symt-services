from unittest.mock import patch

from django.db import transaction
from django.test import TestCase

from client.models import Client
from employee.models import Employee
from organization.models import Organization

from .models import Service
from .selectors import (
    get_active_services,
    get_service_by_id,
    get_services_by_status,
    get_services_for_org,
)
from .services import (
    service_assign_employee,
    service_create,
    service_finalize,
    service_reactivate,
)


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


class ServiceSelectorsTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")
        self.client_obj = Client.objects.create(first_name="Juan", organization=self.org)
        self.client_b = Client.objects.create(first_name="Maria", organization=self.org_b)
        self.service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Servicio A", service_number=1
        )
        self.service_b = Service.objects.create(
            organization=self.org_b, client=self.client_b,
            service_title="Servicio B", service_number=1
        )

    def test_get_services_for_org_returns_only_org_services(self):
        qs = get_services_for_org(org=self.org)
        self.assertIn(self.service, qs)
        self.assertNotIn(self.service_b, qs)

    def test_get_service_by_id_returns_correct_service(self):
        result = get_service_by_id(org=self.org, service_id=self.service.pk)
        self.assertEqual(result, self.service)

    def test_get_service_by_id_raises_if_wrong_org(self):
        with self.assertRaises(Exception):
            get_service_by_id(org=self.org, service_id=self.service_b.pk)

    def test_get_active_services_excludes_cancelled(self):
        self.service.status = Service.Status.Cancelled
        self.service.save()
        qs = get_active_services(org=self.org)
        self.assertNotIn(self.service, qs)

    def test_get_services_by_status_filters_correctly(self):
        qs = get_services_by_status(org=self.org, status=Service.Status.Creating)
        self.assertIn(self.service, qs)
        self.assertNotIn(self.service_b, qs)


class ServiceServicesTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.client_obj = Client.objects.create(first_name="Juan", organization=self.org)
        self.employee = Employee.objects.create(
            organization=self.org, first_name="Ana", last_name="Lopez",
            phone_number="5551234567", chat_id="chat123"
        )

    @patch('service.services.asyncio.run')
    def test_service_create_without_employee(self, mock_run):
        service = service_create(org=self.org, client=self.client_obj, title="Nuevo servicio")
        self.assertEqual(service.organization, self.org)
        self.assertEqual(service.service_number, 1)
        self.assertEqual(service.status, Service.Status.Creating)
        mock_run.assert_not_called()

    @patch('service.services.asyncio.run')
    def test_service_create_with_employee_sends_telegram(self, mock_run):
        service = service_create(
            org=self.org, client=self.client_obj,
            title="Nuevo servicio", employee=self.employee
        )
        self.assertEqual(service.status, Service.Status.Assigned)
        self.assertEqual(mock_run.call_count, 2)

    @patch('service.services.asyncio.run')
    def test_service_create_increments_service_number_per_org(self, mock_run):
        service_create(org=self.org, client=self.client_obj, title="S1")
        service2 = service_create(org=self.org, client=self.client_obj, title="S2")
        self.assertEqual(service2.service_number, 2)

    @patch('service.services.asyncio.run')
    def test_service_assign_employee_sets_assigned(self, mock_run):
        service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Test", service_number=1
        )
        result = service_assign_employee(service=service, employee=self.employee)
        self.assertEqual(result.status, Service.Status.Assigned)
        self.assertEqual(result.employee, self.employee)
        self.assertIsNotNone(result.assigment_date)

    @patch('service.services.asyncio.run')
    def test_service_assign_employee_sets_reassigned_when_had_employee(self, mock_run):
        other_employee = Employee.objects.create(
            organization=self.org, first_name="Bob", last_name="Smith",
            phone_number="5559876543", chat_id="chat456"
        )
        service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Test", service_number=1,
            employee=other_employee, status=Service.Status.Assigned
        )
        result = service_assign_employee(service=service, employee=self.employee)
        self.assertEqual(result.status, Service.Status.Reassigned)

    @patch('service.services.asyncio.run')
    def test_service_assign_employee_sends_telegram(self, mock_run):
        service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Test", service_number=1
        )
        service_assign_employee(service=service, employee=self.employee)
        self.assertEqual(mock_run.call_count, 2)

    def test_service_finalize_sets_cancelled_and_end_date(self):
        service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Test", service_number=1
        )
        result = service_finalize(service=service, summary="Trabajo terminado")
        self.assertEqual(result.status, Service.Status.Cancelled)
        self.assertIsNotNone(result.end_date)
        self.assertEqual(result.summary, "Trabajo terminado")

    def test_service_reactivate_clears_employee_and_resets_status(self):
        service = Service.objects.create(
            organization=self.org, client=self.client_obj,
            service_title="Test", service_number=1,
            employee=self.employee, status=Service.Status.Cancelled
        )
        result = service_reactivate(service=service)
        self.assertEqual(result.status, Service.Status.Creating)
        self.assertIsNone(result.employee)
