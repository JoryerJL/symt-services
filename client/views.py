from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView,  CreateView
from common.views import AdminRequiredMixin

from .forms import ClientForm, AddressForm
from .models import Client

# Create your views here.
class ClientListView(AdminRequiredMixin, ListView):
    model = Client
    template_name = 'client_list.html'
    context_object_name = 'clients'
    ordering = ['-created_at']

class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    template_name = 'client_create.html'
    form_class = ClientForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['client_form'] = self.form_class(
                self.request.POST)
            context['address_form'] = AddressForm(self.request.POST)
        else:
            context['client_form'] = self.form_class()
            context['address_form'] = AddressForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        client_form = context['client_form']
        address_form = context['address_form']
        if client_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            client = client_form.save(commit=False)
            client.address = address
            client.save()
            messages.success(self.request, "Cliente registrado con éxito.")
            return redirect('client_list')
        else:
            return self.render_to_response(self.get_context_data(form=form))


def change_client_status(request, pk):
    client = Client.objects.get(pk=pk)
    if client.is_active:
        client.is_active = False
        messages.error(request, "El cliente ha sido inactivado con exito.")
    else:
        client.is_active = True
        messages.success(request, "El cliente ha sido activado con exito.")
    client.save()
    return redirect('client_list')