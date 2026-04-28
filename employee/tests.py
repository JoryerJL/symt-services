from django.test import TestCase

from organization.models import Organization

from .models import Employee
from .selectors import get_employee_by_chat_id, get_employee_by_phone, get_employees_for_org
from .services import employee_toggle_status, employee_update_chat_id


class EmployeeOrganizationTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", slug="test-org")

    def test_employee_has_organization_field(self):
        field = Employee._meta.get_field('organization')
        self.assertTrue(field.null)
        self.assertTrue(field.blank)
        self.assertEqual(field.related_model, Organization)

    def test_employee_can_belong_to_organization(self):
        emp = Employee.objects.create(
            first_name="Juan", last_name="Perez",
            phone_number="1234567890", organization=self.org
        )
        self.assertEqual(emp.organization, self.org)

    def test_filter_employees_by_organization(self):
        org_b = Organization.objects.create(name="Org B", slug="org-b")
        Employee.objects.create(
            first_name="A", last_name="A", phone_number="1111111111", organization=self.org
        )
        Employee.objects.create(
            first_name="B", last_name="B", phone_number="2222222222", organization=org_b
        )
        result = Employee.objects.filter(organization=self.org)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().first_name, "A")


class EmployeeSelectorsTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")
        self.employee = Employee.objects.create(
            organization=self.org, first_name="Ana", last_name="Lopez",
            phone_number="5551234567", chat_id="chat123"
        )
        self.inactive = Employee.objects.create(
            organization=self.org, first_name="Bob", last_name="Smith",
            phone_number="5559876543", is_active=False
        )
        self.other_org = Employee.objects.create(
            organization=self.org_b, first_name="Carlos", last_name="Reyes",
            phone_number="5550000000"
        )

    def test_get_employee_by_chat_id(self):
        result = get_employee_by_chat_id(chat_id="chat123")
        self.assertEqual(result, self.employee)

    def test_get_employee_by_phone(self):
        result = get_employee_by_phone(phone_number="5551234567")
        self.assertEqual(result, self.employee)

    def test_get_employees_for_org_returns_only_active_in_org(self):
        qs = get_employees_for_org(org=self.org)
        self.assertIn(self.employee, qs)
        self.assertNotIn(self.inactive, qs)
        self.assertNotIn(self.other_org, qs)


class EmployeeServicesTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org A", slug="org-a")
        self.employee = Employee.objects.create(
            organization=self.org, first_name="Ana", last_name="Lopez",
            phone_number="5551234567", chat_id=None
        )

    def test_employee_update_chat_id(self):
        result = employee_update_chat_id(employee=self.employee, chat_id="new_chat_123")
        self.assertEqual(result.chat_id, "new_chat_123")
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.chat_id, "new_chat_123")

    def test_employee_toggle_status_deactivates_active_employee(self):
        result = employee_toggle_status(employee=self.employee)
        self.assertFalse(result.is_active)
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)

    def test_employee_toggle_status_reactivates_inactive_employee(self):
        self.employee.is_active = False
        self.employee.save()
        result = employee_toggle_status(employee=self.employee)
        self.assertTrue(result.is_active)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_active)
