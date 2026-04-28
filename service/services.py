import asyncio

from decouple import config
from django.db.models import Max
from django.utils import timezone

from client.models import Client
from employee.models import Employee
from organization.models import Organization

from .models import Service
from .utils import createMsg, send_confirm_msg, send_msg


def service_create(
    *,
    org: Organization,
    client: Client,
    title: str,
    description: str = None,
    employee: Employee = None,
) -> Service:
    last_num = Service.objects.filter(organization=org).aggregate(
        Max('service_number')
    )['service_number__max'] or 0
    service = Service(
        organization=org,
        client=client,
        service_title=title,
        description=description,
        service_number=last_num + 1,
    )
    if employee:
        service.employee = employee
        service.status = Service.Status.Assigned
        service.assigment_date = timezone.now()
    service.full_clean()
    service.save()
    if employee:
        message = createMsg(service)
        asyncio.run(send_msg(message, employee.chat_id, service.id))
        asyncio.run(send_confirm_msg(message, config("GROUP_CHAT_ID")))
    return service


def service_assign_employee(*, service: Service, employee: Employee) -> Service:
    had_employee = service.employee is not None
    service.employee = employee
    service.status = Service.Status.Reassigned if had_employee else Service.Status.Assigned
    service.assigment_date = timezone.now()
    service.save(update_fields=['employee', 'status', 'assigment_date'])
    message = createMsg(service)
    asyncio.run(send_msg(message, employee.chat_id, service.id))
    asyncio.run(send_confirm_msg(message, config("GROUP_CHAT_ID")))
    return service


def service_finalize(*, service: Service, summary: str = None) -> Service:
    service.status = Service.Status.Cancelled
    service.end_date = timezone.now()
    if summary:
        service.summary = (
            f"{service.summary}\n{summary}".strip() if service.summary else summary
        )
    service.save(update_fields=['status', 'end_date', 'summary'])
    return service


def service_reactivate(*, service: Service) -> Service:
    service.status = Service.Status.Creating
    service.employee = None
    service.save(update_fields=['status', 'employee'])
    return service
