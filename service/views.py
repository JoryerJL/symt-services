import asyncio
import os

from decouple import config
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.views.generic.edit import UpdateView
from weasyprint import HTML
from common.views import AdminRequiredMixin

from service.forms import ServiceForm, AssignEmployeeForm, ServiceSummaryUpdateForm
from service.models import Service
from service.utils import send_msg, createMsg, send_confirm_msg


# Create your views here.
class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'service_list.html'
    context_object_name = 'services'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['assign_employee_form'] = AssignEmployeeForm(
                self.request.POST)
        else:
            context['assign_employee_form'] = AssignEmployeeForm()

        return context

class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    template_name = 'service_create.html'
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['service_form'] = self.form_class(
                self.request.POST)
        else:
            context['service_form'] = self.form_class()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        service_form = context['service_form']
        if service_form.is_valid():
            service = service_form.save(commit=False)
            service.save()
            service.service_number = service.pk
            service.save(update_fields=["service_number"])

            if service.employee :
                service.status = Service.Status.Assigned
                service.assigment_date = timezone.now()
                service.save()
            if service.employee :
                message = createMsg(service)
                asyncio.run(send_msg(message, service.employee.chat_id, service.id))
                asyncio.run(send_confirm_msg(message, config("GROUP_CHAT_ID")))
            messages.success(self.request, "Servicio registrado con éxito.")
            return redirect('services_list')
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class AssignEmployeeView( AdminRequiredMixin, View):
    today = timezone.now().date()
    def post(self, request, *args, **kwargs):
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        if service.employee :
            service_had_employee = True
        else:
            service_had_employee = False
        form = AssignEmployeeForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            service.assigment_date = timezone.now()
            if service_had_employee:
                service.status =  Service.Status.Reassigned
            else:
                service.status = Service.Status.Assigned
            service.save()

            messages.success(request, 'Empleado asignado con éxito.')
            message = createMsg(service)
            asyncio.run(send_msg(message, service.employee.chat_id, service.id))
            asyncio.run(send_confirm_msg(message, config("GROUP_CHAT_ID")))
            if request.POST.get('next'):
                return redirect(request.POST['next'])
            return redirect('services_list')
        else:
            messages.error(request, 'Error al asignar el empleado.')
            return redirect('services_list')

def reactivate_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.status = Service.Status.Creating
    service.employee = None
    service.save()
    messages.success(request, 'Servicio reactivado con éxito.')
    if request.GET.get('next'):
        return redirect(request.GET['next'])
    return redirect('services_list')

class ServiceDetailView(AdminRequiredMixin, DetailView):
    model = Service
    template_name = 'service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        employee = service.employee
        client = service.client

        # # Obtención de credenciales de entorno
        # ftp_host = config("FTP_HOST")
        # ftp_user = config("FTP_USER")
        # ftp_pass = config("FTP_PASS")
        # ftp_path = config("FTP_PATH")
        #
        # # Construcción de la ruta en el FTP
        # ftp_directory = f"{ftp_path}/{service.service_number}-{client.first_name}-{service.created_at.strftime('%Y-%m-%d')}"
        #
        # # Obtener imágenes desde el FTP
        # images = list_images_from_ftp(service)
        #
        # # Construcción de URLs FTP
        # image_urls = [f"ftp://{ftp_user}:{ftp_pass}@{ftp_host}{ftp_directory}/{img}" for img in images]
        #
        # # Agregar datos al contexto
        # context.update({
        #     "FTP_USER": ftp_user,
        #     "FTP_PASS": ftp_pass,
        #     "FTP_HOST": ftp_host,
        #     "FTP_PATH": ftp_path,
        #     "employee": employee,
        #     "client": client,
        #     "images": images,  # Lista de nombres de archivos
        #     "image_urls": image_urls,  # URLs accesibles por el navegador
        # })
        if self.request.POST:
            context['ubication_url'] = reverse_lazy('service_detail')
            context['summary_update_form'] = ServiceSummaryUpdateForm(
                self.request.POST)
            context['assign_employee_form'] = AssignEmployeeForm(
                self.request.POST)
        else:
            context['summary_update_form'] = ServiceSummaryUpdateForm(instance=service)
            context['assign_employee_form'] = AssignEmployeeForm()

        return context

class ServiceSummaryUpdateView(AdminRequiredMixin, View):
    def post(self, request):
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        form = ServiceSummaryUpdateForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resumen del servicio actualizado con éxito.')
            return redirect('service_detail', pk=service_id)
        else:
            messages.error(request, 'Error al actualizar el resumen del servicio.')
            return redirect('service_detail', pk=service_id)
def generate_report_view(request, pk):
    """Vista para generar reporte PDF del servicio"""
    if request.method == 'POST':
        service = get_object_or_404(Service, pk=pk)
        selected_image_ids = request.POST.getlist('selected_images')

        # Validar que se haya seleccionado al menos una imagen
        if not selected_image_ids:
            messages.error(request, 'Debe seleccionar al menos una imagen para generar el reporte.')
            return redirect('service_detail', pk=pk)

        # Obtener las imágenes seleccionadas
        selected_images = service.images.filter(id__in=selected_image_ids)

        # Convertir URLs de imágenes a rutas absolutas para WeasyPrint
        images_with_paths = []
        for image in selected_images:
            if image.image:
                # Construir ruta absoluta de la imagen
                image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
                if os.path.exists(image_path):
                    images_with_paths.append({
                        'image': image,
                        'absolute_path': f'file://{image_path}',
                        'exists': True
                    })
                else:
                    images_with_paths.append({
                        'image': image,
                        'absolute_path': None,
                        'exists': False
                    })
            else:
                images_with_paths.append({
                    'image': image,
                    'absolute_path': None,
                    'exists': False
                })

        # Organizar imágenes en bloques para paginación
        # Primera página: máximo 9 imágenes
        # Páginas siguientes: bloques de 15 imágenes
        image_blocks = []

        if len(images_with_paths) <= 9:
            # Si hay 9 o menos imágenes, todas van en la primera página
            image_blocks.append({
                'is_first_page': True,
                'images': images_with_paths
            })
        else:
            # Primera página con 9 imágenes
            image_blocks.append({
                'is_first_page': True,
                'images': images_with_paths[:9]
            })

            # Páginas siguientes con bloques de 15 imágenes
            remaining_images = images_with_paths[9:]
            for i in range(0, len(remaining_images), 15):
                image_blocks.append({
                    'is_first_page': False,
                    'images': remaining_images[i:i+15]
                })

        # Obtener rutas absolutas de las imágenes estáticas
        static_root = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
        logo_path = os.path.join(static_root, 'images', 'logos', 'SYMT MX.png')
        qr_path = os.path.join(static_root, 'images', 'logos', 'QR.png')

        # Preparar contexto para el template PDF
        context = {
            'service': service,
            'client': service.client,
            'employee': service.employee,
            'image_blocks': image_blocks,
            'logo_path': logo_path,
            'qr_path': qr_path,
        }

        try:
            # Renderizar HTML
            html_string = render_to_string('service_report_pdf.html', context)

            # Generar PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf()

            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="reporte_servicio_{service.service_number}.pdf"'

            return response

        except Exception as e:
            messages.error(request, f'Error al generar el reporte: {str(e)}')
            return redirect('service_detail', pk=pk)

    return redirect('service_detail', pk=pk)
