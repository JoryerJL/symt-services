from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from common.views import AdminRequiredMixin
from .forms import EmployeeForm
from .models import Employee

# Create your views here.
class EmployeeListView(AdminRequiredMixin, ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'
    ordering = ['-created_at']

class EmployeeCreateView(AdminRequiredMixin, CreateView):
    model = Employee
    template_name = 'employee_create.html'
    form_class = EmployeeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['employee_form'] = self.form_class(
                self.request.POST)
        else:
            context['employee_form'] = self.form_class()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        employee_form = context['employee_form']
        if employee_form.is_valid():
            service = employee_form.save(commit=False)
            service.save()
            messages.success(self.request, "Empleado registrado con éxito.")
            return redirect('employee_list')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


def change_employee_status(request, pk):
    employee = Employee.objects.get(pk=pk)
    if employee.is_active:
        employee.is_active = False
        messages.error(request, "El empleado ha sido inactivado con exito.")
    else:
        employee.is_active = True
        messages.success(request, "El empleado ha sido activado con exito.")
    employee.save()
    return redirect('employee_list')