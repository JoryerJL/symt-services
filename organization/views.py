from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from common.views import SuperAdminRequiredMixin

from .forms import AssignUserToOrganizationForm, OrganizationCreateForm, OrganizationUpdateForm
from .selectors import (
    get_organization_by_slug,
    get_organization_members,
    get_organization_stats,
    get_organizations_with_summary,
)
from .services import (
    organization_assign_user,
    organization_create,
    organization_toggle_active,
    organization_update_name,
)


class OrganizationListView(SuperAdminRequiredMixin, ListView):
    template_name = 'org_list.html'
    context_object_name = 'organizations'

    def get_queryset(self):
        return get_organizations_with_summary()


class OrganizationCreateView(SuperAdminRequiredMixin, CreateView):
    template_name = 'org_create.html'
    form_class = OrganizationCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_form'] = kwargs.get('form') or OrganizationCreateForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OrganizationCreateForm(request.POST)
        if form.is_valid():
            organization = organization_create(name=form.cleaned_data['name'])
            messages.success(request, 'Organización creada con éxito.')
            return redirect('organization_detail', slug=organization.slug)
        return self.render_to_response(self.get_context_data(form=form))


class OrganizationUpdateView(SuperAdminRequiredMixin, UpdateView):
    template_name = 'org_edit.html'
    form_class = OrganizationUpdateForm
    context_object_name = 'organization'

    def get_object(self):
        return get_organization_by_slug(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_form'] = kwargs.get('form') or OrganizationUpdateForm(instance=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        organization = self.get_object()
        form = OrganizationUpdateForm(request.POST, instance=organization)
        if form.is_valid():
            organization_update_name(
                organization=organization,
                name=form.cleaned_data['name'],
            )
            messages.success(request, 'Organización actualizada con éxito.')
            return redirect('organization_detail', slug=organization.slug)
        return self.render_to_response(self.get_context_data(form=form))


class OrganizationDetailView(SuperAdminRequiredMixin, DetailView):
    template_name = 'org_detail.html'
    context_object_name = 'organization'

    def get_object(self):
        return get_organization_by_slug(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.get_object()
        context['stats'] = get_organization_stats(organization=organization)
        context['members'] = get_organization_members(organization=organization)
        context['assign_user_form'] = kwargs.get('assign_user_form') or AssignUserToOrganizationForm()
        return context


class OrganizationToggleView(SuperAdminRequiredMixin, View):
    def post(self, request, slug):
        organization = get_organization_by_slug(slug=slug)
        organization_toggle_active(organization=organization)
        state = 'activada' if organization.is_active else 'desactivada'
        messages.success(request, f'Organización {state} con éxito.')
        return redirect('organization_detail', slug=organization.slug)


class OrganizationAssignUserView(SuperAdminRequiredMixin, View):
    def post(self, request, slug):
        organization = get_organization_by_slug(slug=slug)
        form = AssignUserToOrganizationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            try:
                organization_assign_user(organization=organization, user=user)
            except ValueError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, 'Usuario asignado con éxito.')
            return redirect('organization_detail', slug=organization.slug)

        submitted_user_id = request.POST.get('user')
        if submitted_user_id:
            user = User.objects.filter(pk=submitted_user_id).first()
            if user and hasattr(user, 'profile'):
                messages.error(request, 'El usuario ya tiene una organización asignada.')
                return redirect('organization_detail', slug=organization.slug)

        messages.error(request, 'Selecciona un usuario disponible para asignar.')
        detail_view = OrganizationDetailView()
        detail_view.setup(request, slug=slug)
        detail_view.object = organization
        return detail_view.render_to_response(
            detail_view.get_context_data(assign_user_form=form)
        )
