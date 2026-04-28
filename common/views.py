from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(AccessMixin):
    """ Mixin para restringir el acceso solo a usuarios en el grupo 'owner'. """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.groups.filter(name="admin").exists():
            raise PermissionDenied(
                "No tienes permiso para acceder a esta página."
            )
        return super().dispatch(request, *args, **kwargs)