from django import forms
from django.contrib.auth.models import User

from .models import Organization


class OrganizationCreateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']
        labels = {
            'name': 'Nombre de la organización',
        }


class OrganizationUpdateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']
        labels = {
            'name': 'Nombre de la organización',
        }


class AssignUserToOrganizationForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Usuario',
        empty_label='Selecciona un usuario',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(profile__isnull=True).order_by('username')
