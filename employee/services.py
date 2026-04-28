from .models import Employee


def employee_update_chat_id(*, employee: Employee, chat_id: str) -> Employee:
    employee.chat_id = chat_id
    employee.save(update_fields=['chat_id'])
    return employee


def employee_toggle_status(*, employee: Employee) -> Employee:
    employee.is_active = not employee.is_active
    employee.save(update_fields=['is_active'])
    return employee
