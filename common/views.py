from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.groups.filter(name="admin").exists():
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        try:
            request.organization = request.user.profile.organization
        except Exception:
            raise PermissionDenied("Tu usuario no tiene una organización asignada.")
        return super().dispatch(request, *args, **kwargs)