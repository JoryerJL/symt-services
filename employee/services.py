from organization.models import Organization

from .models import Employee


def employee_create(
    *,
    org: Organization,
    first_name: str,
    last_name: str,
    phone_number: str,
    chat_id: str = None,
) -> Employee:
    employee = Employee(
        organization=org,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        chat_id=chat_id,
    )
    employee.full_clean()
    employee.save()
    return employee


def employee_update_chat_id(*, employee: Employee, chat_id: str) -> Employee:
    employee.chat_id = chat_id
    employee.save(update_fields=['chat_id'])
    return employee


def employee_toggle_status(*, employee: Employee) -> Employee:
    employee.is_active = not employee.is_active
    employee.save(update_fields=['is_active'])
    return employee
