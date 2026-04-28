from django.db.models import QuerySet

from organization.models import Organization

from .models import Employee


def get_employee_by_chat_id(*, chat_id: str) -> Employee:
    return Employee.objects.get(chat_id=chat_id)


def get_employee_by_phone(*, phone_number: str) -> Employee:
    return Employee.objects.get(phone_number=phone_number)


def get_employee_by_pk(*, employee_id: int) -> Employee:
    return Employee.objects.get(pk=employee_id)


def get_employee_by_id(*, org: Organization, employee_id: int) -> Employee:
    return Employee.objects.get(organization=org, pk=employee_id)


def get_employees_for_org(*, org: Organization) -> QuerySet:
    return Employee.objects.filter(organization=org, is_active=True)
