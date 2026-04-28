from .models import Client, Address
from django import forms

class ClientForm(forms.ModelForm):
    class Meta:
        first_name = forms.CharField(help_text="Escribe el nombre del empleado", label='Nombre', required=True,
                                     max_length=100)
        company = forms.CharField(help_text="Escribe el nombre de la empresa", label='Empresa', required=True,
                                    max_length=100)
        phone_number = forms.CharField(help_text="Escribe el numero de telefono", label='Telefono', required=True,
                                    max_length=100)
        responsible = forms.CharField(help_text="Escribe el nombre del responsable", label='Responsable', required=True,
                                      max_length=100)
        model = Client
        fields = ['first_name', 'company', 'phone_number', 'responsible']
        labels = {
            'first_name' : 'Nombre',
            'company'    : 'Empresa',
            'phone_number': 'Telefono',
            'responsible': 'Responsable',
        }
class AddressForm(forms.ModelForm):
    class Meta:
        street = forms.CharField(help_text="Escribe la calle", label='Calle', required=True,
                                     max_length=100)
        number = forms.CharField(help_text="Escribe el numero", label='Numero', required=True,
                                    max_length=100)
        colony = forms.CharField(help_text="Escribe la colonia", label='Colonia', required=True,
                                    max_length=100)
        city = forms.CharField(help_text="Escribe la ciudad", label='Ciudad', required=True,
                                    max_length=100)
        state = forms.CharField(help_text="Escribe el estado", label='Estado', required=True,
                                    max_length=100)
        country = forms.CharField(help_text="Escribe el pais", label='Pais', required=True,
                                    max_length=100)
        postal_code = forms.CharField(help_text="Escribe el codigo postal", label='Codigo postal', required=True,
                                    max_length=100)

        model = Address
        fields = ['street', 'number', 'colony','city', 'state', 'country', 'postal_code']
        labels = {
            'street' : 'Calle',
            'number'  : 'Numero',
            'colony': 'Colonia',
            'city'    : 'Ciudad',
            'state': 'Estado',
            'country': 'Pais',
            'postal_code': 'Codigo postal',
        }