from django.db import models

from client.models import Client
from common.models import CommonBaseModel
from employee.models import Employee
from organization.models import Organization


class Service(CommonBaseModel):
    class Status(models.IntegerChoices):
        Creating = 0, 'Creado'
        Active = 1, 'Confirmado'
        Cancelled = 2, 'Finalizado'
        Assigned = 3, 'Asignado'
        Reassigned = 4, 'Reasignado'

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='services', null=True, blank=True
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client")
    service_number = models.PositiveIntegerField(null=True, blank=True)
    service_title = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="employee", null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=Status.Creating)
    assigment_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    request_methods = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('organization', 'service_number')

    def __str__(self):
        return f"Servicio {self.service_number} - {self.client}"

class ServiceImage(CommonBaseModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="service_images/", max_length=200)
    nas_url = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"Imagen del Servicio {self.service.service_number} - {self.image.name}"