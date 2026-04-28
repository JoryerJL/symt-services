from django.db import models
from common.models import CommonBaseModel

class Address(CommonBaseModel):
    street = models.CharField("Calle",max_length=100)
    number = models.CharField("Numero",max_length=100)
    colony = models.CharField("Colonia",max_length=100)
    city = models.CharField("Ciudad",max_length=100)
    state = models.CharField("Estado",max_length=100)
    country = models.CharField("Pais",max_length=100)
    postal_code = models.CharField("Codigo postal",max_length=100)

    def __str__(self):
        return f'{self.street} {self.number}, {self.colony}, {self.city}, {self.state}, {self.country}, {self.postal_code}'

# Create your models here.
class Client(CommonBaseModel):
    first_name = models.CharField("Nombre",max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField("Empresa",max_length=100, null=True, blank=True)
    phone_number = models.CharField("Telefono",max_length=100, null=True, blank=True)
    responsible = models.CharField("Responsable",max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.first_name}'

    def full_name(self):
        return f'{self.first_name}'
