from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, CreateView

from common.views import AdminRequiredMixin
from client.selectors import get_clients_for_org
from client.services import client_create, client_toggle_status
from .forms import ClientForm, AddressForm
from .models import Client


class ClientListView(AdminRequiredMixin, ListView):
    template_name = 'client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return get_clients_for_org(org=self.request.organization)


class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'client_create.html'
    form_class = ClientForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['client_form'] = ClientForm(self.request.POST)
            context['address_form'] = AddressForm(self.request.POST)
        else:
            context['client_form'] = ClientForm()
            context['address_form'] = AddressForm()
        return context

    def post(self, request, *args, **kwargs):
        client_form = ClientForm(request.POST)
        address_form = AddressForm(request.POST)
        if client_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            client_create(
                org=request.organization,
                first_name=client_form.cleaned_data['first_name'],
                company=client_form.cleaned_data.get('company'),
                phone_number=client_form.cleaned_data.get('phone_number'),
                responsible=client_form.cleaned_data.get('responsible'),
                address=address,
            )
            messages.success(request, "Cliente registrado con éxito.")
            return redirect('client_list')
        return self.render_to_response(self.get_context_data())


class ChangeClientStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        client = Client.objects.get(organization=request.organization, pk=pk)
        client_toggle_status(client=client)
        if client.is_active:
            messages.success(request, "El cliente ha sido activado con éxito.")
        else:
            messages.error(request, "El cliente ha sido inactivado con éxito.")
        return redirect('client_list')
