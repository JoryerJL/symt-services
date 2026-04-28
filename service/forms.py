from client.models import Client
from employee.models import Employee
from service.models import Service
from django import forms


class ServiceForm(forms.ModelForm):
    service_title = forms.CharField(help_text="Escribe el titulo del servicio",label='Titulo del servicio', max_length=100)
    description = forms.CharField(help_text="Escribe la descripcion del servicio",label='Descripcion del servicio', max_length=500)
    class Meta:
        model = Service
        fields = ['client', 'employee','service_title', 'description', 'request_methods']
        labels = {
            'client': 'Cliente',
            'employee': 'Empleado',
            'service_title': 'Titulo del servicio',
            'description': 'Descripcion del servicio',
            'request_methods' : 'Medio de solicitud',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(is_active=True)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)

class ServiceSummaryUpdateForm(forms.ModelForm):
    summary = forms.CharField(widget=forms.Textarea, help_text="Escribe el resumen del servicio", label='Resumen del servicio', max_length=1000)

    class Meta:
        model = Service
        fields = ['summary']
        labels = {
            'summary': 'Resumen del servicio',
        }

class AssignEmployeeForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['employee']
        labels = {
            'employee': 'Empleado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)