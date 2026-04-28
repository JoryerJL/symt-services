from django.db import models
from common.models import CommonBaseModel

# Create your models here.
class Employee(CommonBaseModel):
    first_name = models.CharField("Nombre",max_length=100)
    last_name = models.CharField("Apellido",max_length=100)
    phone_number = models.CharField("Numero telefonico",max_length=100)
    chat_id = models.CharField("Chat ID",max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.first_name} - {self.phone_number}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'