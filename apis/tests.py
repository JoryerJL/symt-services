from rest_framework import status
from rest_framework.test import APITestCase

from client.models import Client
from employee.models import Employee
from organization.models import Organization
from service.models import Service


class EmployeeApiTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org API", slug="org-api")
        self.employee = Employee.objects.create(
            organization=self.org,
            first_name="Ana",
            last_name="Lopez",
            phone_number="5551234567",
            chat_id="chat-123",
        )

    def test_list_by_chat_id_returns_employee_with_organization_context(self):
        response = self.client.get("/api/employee/", {"chat_id": "chat-123"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.employee.id)
        self.assertEqual(response.data["organization_id"], self.org.id)
        self.assertEqual(response.data["organization_slug"], self.org.slug)

    def test_list_by_phone_number_uses_last_ten_digits(self):
        response = self.client.get("/api/employee/", {"phone_number": "5215551234567"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.employee.id)

    def test_list_requires_chat_id_or_phone_number(self):
        response = self.client.get("/api/employee/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "chat_id or phone_number is required")

    def test_list_returns_404_when_employee_does_not_exist(self):
        response = self.client.get("/api/employee/", {"chat_id": "missing"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Not Found")

    def test_put_updates_only_chat_id_via_service_layer(self):
        response = self.client.put(
            f"/api/employee/{self.employee.id}/",
            {
                "id": self.employee.id,
                "first_name": "SHOULD-NOT-CHANGE",
                "last_name": self.employee.last_name,
                "phone_number": self.employee.phone_number,
                "chat_id": "chat-999",
                "organization_id": self.org.id,
                "organization_slug": self.org.slug,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.chat_id, "chat-999")
        self.assertEqual(self.employee.first_name, "Ana")
        self.assertEqual(response.data["organization_slug"], self.org.slug)

    def test_put_requires_chat_id(self):
        response = self.client.put(
            f"/api/employee/{self.employee.id}/",
            {
                "id": self.employee.id,
                "first_name": self.employee.first_name,
                "last_name": self.employee.last_name,
                "phone_number": self.employee.phone_number,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["chat_id"], ["This field is required."])


class ServiceApiTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org Service", slug="org-service")
        self.client_obj = Client.objects.create(
            organization=self.org,
            first_name="Cliente API",
        )
        self.service = Service.objects.create(
            organization=self.org,
            client=self.client_obj,
            service_title="Servicio API",
            service_number=1,
            summary="Resumen previo",
        )

    def test_retrieve_returns_service_by_id(self):
        response = self.client.get(f"/api/service/{self.service.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.service.id)
        self.assertEqual(response.data["service_number"], self.service.service_number)

    def test_patch_appends_summary_and_updates_status(self):
        response = self.client.patch(
            f"/api/service/{self.service.id}/",
            {
                "status": Service.Status.Cancelled,
                "summary": "Resumen nuevo",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, Service.Status.Cancelled)
        self.assertEqual(self.service.summary, "Resumen previo\nResumen nuevo")

    def test_retrieve_returns_404_for_missing_service(self):
        response = self.client.get("/api/service/9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Not Found")


class ClientApiTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Org Client", slug="org-client")
        self.client_obj = Client.objects.create(
            organization=self.org,
            first_name="Cliente API",
        )

    def test_retrieve_returns_client_by_id(self):
        response = self.client.get(f"/api/client/{self.client_obj.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.client_obj.id)
        self.assertEqual(response.data["first_name"], self.client_obj.first_name)

    def test_list_is_blocked_to_avoid_global_client_exposure(self):
        response = self.client.get("/api/client/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "client detail endpoint only")
