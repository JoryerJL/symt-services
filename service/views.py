import os

from decouple import config
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.conf import settings
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView
from django.urls.base import reverse_lazy
from weasyprint import HTML

from common.views import AdminRequiredMixin
from service.forms import ServiceForm, AssignEmployeeForm, ServiceSummaryUpdateForm
from service.selectors import get_service_by_id, get_services_for_org
from service.services import (
    service_assign_employee,
    service_create,
    service_finalize,
    service_reactivate,
)


class ServiceListView(AdminRequiredMixin, ListView):
    model = None
    template_name = 'service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return get_services_for_org(org=self.request.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assign_employee_form'] = AssignEmployeeForm(
            self.request.POST if self.request.POST else None
        )
        return context


class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = None
    template_name = 'service_create.html'
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_form'] = ServiceForm(self.request.POST if self.request.POST else None)
        return context

    def post(self, request, *args, **kwargs):
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = service_create(
                org=request.organization,
                client=form.cleaned_data['client'],
                title=form.cleaned_data['service_title'],
                description=form.cleaned_data.get('description'),
                employee=form.cleaned_data.get('employee'),
            )
            messages.success(request, "Servicio registrado con éxito.")
            return redirect('services_list')
        return self.render_to_response(self.get_context_data(form=form))


class AssignEmployeeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service_id')
        service = get_service_by_id(org=request.organization, service_id=service_id)
        form = AssignEmployeeForm(request.POST, instance=service)
        if form.is_valid():
            service_assign_employee(
                service=service,
                employee=form.cleaned_data['employee'],
            )
            messages.success(request, 'Empleado asignado con éxito.')
            if request.POST.get('next'):
                return redirect(request.POST['next'])
            return redirect('services_list')
        messages.error(request, 'Error al asignar el empleado.')
        return redirect('services_list')


class ReactivateServiceView(AdminRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = get_service_by_id(org=request.organization, service_id=pk)
        service_reactivate(service=service)
        messages.success(request, 'Servicio reactivado con éxito.')
        if request.GET.get('next'):
            return redirect(request.GET['next'])
        return redirect('services_list')


class ServiceDetailView(AdminRequiredMixin, DetailView):
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_object(self):
        return get_service_by_id(org=self.request.organization, service_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        if self.request.POST:
            context['summary_update_form'] = ServiceSummaryUpdateForm(self.request.POST)
            context['assign_employee_form'] = AssignEmployeeForm(self.request.POST)
        else:
            context['summary_update_form'] = ServiceSummaryUpdateForm(instance=service)
            context['assign_employee_form'] = AssignEmployeeForm()
        return context


class ServiceSummaryUpdateView(AdminRequiredMixin, View):
    def post(self, request):
        service_id = request.POST.get('service_id')
        service = get_service_by_id(org=request.organization, service_id=service_id)
        form = ServiceSummaryUpdateForm(request.POST, instance=service)
        if form.is_valid():
            service_finalize(service=service, summary=form.cleaned_data.get('summary'))
            messages.success(request, 'Resumen del servicio actualizado con éxito.')
            return redirect('service_detail', pk=service_id)
        messages.error(request, 'Error al actualizar el resumen del servicio.')
        return redirect('service_detail', pk=service_id)


class GenerateReportView(AdminRequiredMixin, View):
    def post(self, request, pk):
        service = get_service_by_id(org=request.organization, service_id=pk)
        selected_image_ids = request.POST.getlist('selected_images')

        if not selected_image_ids:
            messages.error(request, 'Debe seleccionar al menos una imagen para generar el reporte.')
            return redirect('service_detail', pk=pk)

        selected_images = service.images.filter(id__in=selected_image_ids)

        images_with_paths = []
        for image in selected_images:
            if image.image:
                image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
                images_with_paths.append({
                    'image': image,
                    'absolute_path': f'file://{image_path}' if os.path.exists(image_path) else None,
                    'exists': os.path.exists(image_path),
                })
            else:
                images_with_paths.append({'image': image, 'absolute_path': None, 'exists': False})

        image_blocks = []
        if len(images_with_paths) <= 9:
            image_blocks.append({'is_first_page': True, 'images': images_with_paths})
        else:
            image_blocks.append({'is_first_page': True, 'images': images_with_paths[:9]})
            remaining = images_with_paths[9:]
            for i in range(0, len(remaining), 15):
                image_blocks.append({'is_first_page': False, 'images': remaining[i:i + 15]})

        static_root = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
        context = {
            'service': service,
            'client': service.client,
            'employee': service.employee,
            'image_blocks': image_blocks,
            'logo_path': os.path.join(static_root, 'images', 'logos', 'SYMT MX.png'),
            'qr_path': os.path.join(static_root, 'images', 'logos', 'QR.png'),
        }

        try:
            html_string = render_to_string('service_report_pdf.html', context)
            pdf = HTML(string=html_string).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'inline; filename="reporte_servicio_{service.service_number}.pdf"'
            )
            return response
        except Exception as e:
            messages.error(request, f'Error al generar el reporte: {str(e)}')
            return redirect('service_detail', pk=pk)

    def get(self, request, pk):
        return redirect('service_detail', pk=pk)
