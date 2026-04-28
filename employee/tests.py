from django.test import TestCase

from organization.models import Organization

from .models import Employee


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
