from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, CreateView

from common.views import AdminRequiredMixin
from employee.selectors import get_employees_for_org
from employee.services import employee_toggle_status
from .forms import EmployeeForm
from .models import Employee


class EmployeeListView(AdminRequiredMixin, ListView):
    template_name = 'employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return get_employees_for_org(org=self.request.organization)


class EmployeeCreateView(AdminRequiredMixin, CreateView):
    model = Employee
    template_name = 'employee_create.html'
    form_class = EmployeeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_form'] = EmployeeForm(self.request.POST if self.request.POST else None)
        return context

    def post(self, request, *args, **kwargs):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.organization = request.organization
            employee.save()
            messages.success(request, "Empleado registrado con éxito.")
            return redirect('employee_list')
        return self.render_to_response(self.get_context_data(form=form))


class ChangeEmployeeStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        employee = Employee.objects.get(organization=request.organization, pk=pk)
        employee_toggle_status(employee=employee)
        if employee.is_active:
            messages.success(request, "El empleado ha sido activado con éxito.")
        else:
            messages.error(request, "El empleado ha sido inactivado con éxito.")
        return redirect('employee_list')
