from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):

    class Meta:
        first_name = forms.CharField(help_text="Escribe el nombre del empleado",label='Nombre', required=True, max_length=100)
        last_name = forms.CharField(help_text="Escribe el apellido del empleado",label='Apellido', required=True, max_length=100)
        phone_number = forms.CharField(help_text="Escribe el numero telefonico del empleado",required=True, label='Numero telefonico', max_length=12)
        chat_id = forms.CharField(help_text="Escribe el chat id de telegram del empleado", required=False, label='Chat ID', max_length=15)
        model = Employee
        fields = 'first_name', 'last_name', 'phone_number', 'chat_id'
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone_number': 'Numero telefonico',
            'chat_id': 'Chat ID'
        }