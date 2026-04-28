# Plan de Implementación: SaaS Multi-Organización

**Iniciado:** 2026-04-27  
**Objetivo:** Convertir symt-services de single-tenant a SaaS donde cada organización solo ve sus propios datos.

> Para contexto de decisiones de diseño, ver [decisions.md](./decisions.md).  
> Para diagramas de arquitectura, ver [architecture.md](./architecture.md).

---

## Instrucciones para agentes

Si eres un agente retomando este trabajo:
1. Lee los checkboxes abajo y encuentra la primera fase incompleta.
2. Lee la sección completa de esa fase (archivos, patrón, notas).
3. Lee `decisions.md` si tienes dudas de diseño — las decisiones ya están tomadas.
4. Al terminar una fase, marca su checkbox y anota cualquier descubrimiento en `decisions.md`.

---

## Estado de las fases

- [x] Fase 1 — Estructura `docs/`
- [x] Fase 2 — App `organization`: modelo + migraciones
- [x] Fase 3 — UserProfile: vincular User ↔ Organization
- [ ] Fase 4 — FK `organization` en Employee, Client, Service
- [ ] Fase 5 — Selectors + Service Layer
- [ ] Fase 6 — Vistas web: delgadas, usan selectors + services
- [ ] Fase 7 — API (DRF): ViewSets usan selectors + services
- [ ] Fase 8 — Bot central multi-org
- [ ] Fase 9 — Panel super-admin para gestión de organizaciones

---

## Fase 1 — Estructura `docs/` ✅

**Estado:** COMPLETADA

Archivos creados:
- `docs/README.md`
- `docs/implementation-plan.md` (este archivo)
- `docs/architecture.md`
- `docs/decisions.md`

---

## Fase 2 — App `organization`: modelo + migraciones

**Objetivo:** Crear la nueva Django app con el modelo `Organization`.

**Archivos a crear:**
```
organization/
├── __init__.py
├── apps.py
├── models.py
├── admin.py
└── migrations/
    └── __init__.py
```

**Modificar:**
- `BotPhotosSYMT/settings.py` → agregar `'organization'` a `INSTALLED_APPS`

**Modelo a implementar:**
```python
# organization/models.py
from django.db import models
from common.models import CommonBaseModel

class Organization(CommonBaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
```

**Verificación:**
```bash
python manage.py makemigrations organization
python manage.py migrate
# Debe crear tabla organization_organization sin errores
```

---

## Fase 3 — UserProfile: vincular User ↔ Organization

**Objetivo:** Cada usuario Django tiene un perfil que lo vincula a una organización.

**Archivos a modificar:**
- `organization/models.py` → agregar `UserProfile`
- `organization/admin.py` → inline de UserProfile en UserAdmin

**Modelo a agregar:**
```python
# organization/models.py (agregar después de Organization)
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )

    def __str__(self):
        return f"{self.user.username} — {self.organization.name}"
```

**Admin (inline para asignar org al crear user):**
```python
# organization/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Organization, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Organization)
```

**Verificación:**
```bash
python manage.py makemigrations organization
python manage.py migrate
# Acceder a /admin/, editar un User y ver el inline de UserProfile
```

---

## Fase 4 — FK `organization` en Employee, Client, Service

**Objetivo:** Vincular cada entidad de negocio a una organización.

**IMPORTANTE:** El campo se agrega nullable primero para no romper data existente.

### Employee
```python
# employee/models.py — agregar campo:
from organization.models import Organization

class Employee(CommonBaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='employees', null=True, blank=True  # nullable en migración inicial
    )
    # ... resto de campos sin cambios
```

### Client
```python
# client/models.py — agregar en Client (NO en Address):
from organization.models import Organization

class Client(CommonBaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='clients', null=True, blank=True
    )
    # ... resto de campos sin cambios
```

### Service
```python
# service/models.py — cambios:
from organization.models import Organization

class Service(CommonBaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='services', null=True, blank=True
    )
    # Eliminar: service_number = models.PositiveIntegerField(unique=True, ...)
    # Reemplazar con:
    service_number = models.PositiveIntegerField(null=True, blank=True)
    # ... resto de campos sin cambios

    class Meta:
        unique_together = ('organization', 'service_number')
```

**Verificación:**
```bash
python manage.py makemigrations employee client service
python manage.py migrate
python manage.py shell
>>> from employee.models import Employee
>>> Employee._meta.get_field('organization')  # debe existir
```

---

## Fase 5 — Selectors + Service Layer

**Referencia patrón:** https://github.com/HackSoftware/Django-Styleguide

**Concepto:** Funciones puras que no saben de HTTP. Views las llaman, no hacen queries directas.

### service/selectors.py
```python
from django.db.models import QuerySet
from organization.models import Organization
from .models import Service

def get_services_for_org(*, org: Organization) -> QuerySet:
    return Service.objects.filter(organization=org).order_by('-created_at')

def get_service_by_id(*, org: Organization, service_id: int) -> Service:
    return Service.objects.get(organization=org, pk=service_id)

def get_active_services(*, org: Organization) -> QuerySet:
    return get_services_for_org(org=org).exclude(status=Service.Status.Cancelled)

def get_services_by_status(*, org: Organization, status: int) -> QuerySet:
    return get_services_for_org(org=org).filter(status=status)
```

### service/services.py
```python
from django.db.models import Max
from django.utils import timezone
from organization.models import Organization
from client.models import Client
from employee.models import Employee
from .models import Service

def service_create(*, org: Organization, client: Client, title: str,
                   description: str = None, employee=None) -> Service:
    last_num = Service.objects.filter(organization=org).aggregate(
        Max('service_number'))['service_number__max'] or 0
    service = Service(
        organization=org, client=client,
        service_title=title, description=description,
        service_number=last_num + 1,
    )
    if employee:
        service.employee = employee
        service.status = Service.Status.Assigned
        service.assigment_date = timezone.now()
    service.full_clean()
    service.save()
    return service

def service_assign_employee(*, service: Service, employee: Employee) -> Service:
    service.employee = employee
    service.status = Service.Status.Assigned
    service.assigment_date = timezone.now()
    service.full_clean()
    service.save(update_fields=['employee', 'status', 'assigment_date'])
    return service

def service_finalize(*, service: Service, summary: str = None) -> Service:
    service.status = Service.Status.Cancelled
    service.end_date = timezone.now()
    if summary:
        service.summary = (service.summary + f"\n{summary}").strip() if service.summary else summary
    service.save(update_fields=['status', 'end_date', 'summary'])
    return service

def service_reactivate(*, service: Service) -> Service:
    service.status = Service.Status.Creating
    service.employee = None
    service.save(update_fields=['status', 'employee'])
    return service
```

### employee/selectors.py
```python
from django.db.models import QuerySet
from organization.models import Organization
from .models import Employee

def get_employee_by_chat_id(*, chat_id: str) -> Employee:
    return Employee.objects.get(chat_id=chat_id)

def get_employee_by_phone(*, phone_number: str) -> Employee:
    return Employee.objects.get(phone_number=phone_number)

def get_employees_for_org(*, org: Organization) -> QuerySet:
    return Employee.objects.filter(organization=org, is_active=True)
```

### employee/services.py
```python
from .models import Employee

def employee_update_chat_id(*, employee: Employee, chat_id: str) -> Employee:
    employee.chat_id = chat_id
    employee.save(update_fields=['chat_id'])
    return employee
```

### client/selectors.py
```python
from django.db.models import QuerySet
from organization.models import Organization
from .models import Client

def get_clients_for_org(*, org: Organization) -> QuerySet:
    return Client.objects.filter(organization=org, is_active=True)

def get_client_by_id(*, org: Organization, client_id: int) -> Client:
    return Client.objects.get(organization=org, pk=client_id)
```

### client/services.py
```python
from organization.models import Organization
from .models import Client, Address

def client_create(*, org: Organization, first_name: str, company: str = None,
                  phone_number: str = None, responsible: str = None,
                  address: Address = None) -> Client:
    client = Client(
        organization=org, first_name=first_name,
        company=company, phone_number=phone_number,
        responsible=responsible, address=address,
    )
    client.full_clean()
    client.save()
    return client
```

**Verificación:**
```bash
python manage.py shell
>>> from service.selectors import get_services_for_org
>>> from organization.models import Organization
>>> org = Organization.objects.first()
>>> get_services_for_org(org=org)  # debe retornar QuerySet vacío o con servicios de esa org
```

---

## Fase 6 — Vistas web: delgadas, usan selectors + services

**Objetivo:** Eliminar queries directas de views. Todo pasa por selectors/services.

**Modificar `common/views.py`:**
```python
class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.groups.filter(name="admin").exists():
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        # Agregar org al request para que todas las views lo usen:
        try:
            request.organization = request.user.profile.organization
        except Exception:
            raise PermissionDenied("Tu usuario no tiene una organización asignada.")
        return super().dispatch(request, *args, **kwargs)
```

**Patrón para service/views.py:**
```python
from service.selectors import get_services_for_org, get_service_by_id, get_active_services
from service.services import service_create, service_assign_employee, service_finalize, service_reactivate

class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return get_services_for_org(org=self.request.organization)
```

**Archivos a modificar:**
- `common/views.py` — inyectar `request.organization`
- `service/views.py` — reemplazar queries directas por selectors/services
- `employee/views.py` — reemplazar queries directas
- `client/views.py` — reemplazar queries directas

**Verificación:** Login con user de Org A, verificar que solo aparecen servicios de Org A.

---

## Fase 7 — API (DRF): ViewSets usan selectors + services

**Objetivo:** Los ViewSets del bot también filtran por org.

**Nota especial:** El endpoint `GET /api/employee/?chat_id=X` es una búsqueda GLOBAL (bootstrap de auth del bot). Debe incluir `organization.slug` y `organization.id` en la respuesta.

**apis/employee/serializers.py — agregar org:**
```python
class EmployeeSerializer(serializers.ModelSerializer):
    organization_slug = serializers.CharField(source='organization.slug', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'chat_id', 'organization_slug']
```

**apis/employee/views.py:**
```python
from employee.selectors import get_employee_by_chat_id, get_employee_by_phone
from employee.services import employee_update_chat_id

class EmployeeViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        chat_id = request.query_params.get('chat_id')
        phone_number = request.query_params.get('phone_number')
        if chat_id:
            employee = get_employee_by_chat_id(chat_id=chat_id)
        elif phone_number:
            employee = get_employee_by_phone(phone_number=phone_number[-10:])
        # ... resto igual
```

**Verificación:**
```bash
curl http://localhost:8000/api/employee/?chat_id=123
# Respuesta debe incluir organization_slug
```

---

## Fase 8 — Bot central multi-org

**Objetivo:** El bot detecta la org del empleado y usa esa org para aislar FTP y servicios.

**Cambios en `PhotosBot.py`:**

1. `active_service[chat_id]` cambia de `str` a `dict`:
```python
# Antes:
active_service[chat_id] = folder_name  # "123-ClienteX-2025-01-01"

# Después:
active_service[chat_id] = {
    "org_slug": employee['organization_slug'],
    "folder": folder_name  # "123-ClienteX-2025-01-01"
}
```

2. FTP usa org prefix:
```python
def upload_a_ftp(local_name, org_slug, service_folder, remote_name):
    ftp = connect_ftp()
    ftp.cwd(f"{FTP_PATH}/{org_slug}/{service_folder}")
    with open(local_name, "rb") as file:
        ftp.storbinary(f"STOR {remote_name}", file)
    ftp.quit()
```

3. `verify_or_create_ftp_folder` crea carpeta de org si no existe:
```python
def verify_or_create_ftp_folder(org_slug, folder_name):
    ftp = connect_ftp()
    # Crear org folder si no existe
    org_path = f"{FTP_PATH}/{org_slug}"
    try:
        ftp.cwd(org_path)
    except ftplib.error_perm:
        ftp.mkd(org_path)
        ftp.cwd(org_path)
    # Crear service folder
    try:
        ftp.cwd(folder_name)
    except ftplib.error_perm:
        ftp.mkd(folder_name)
    ftp.quit()
```

4. `nas_url` en ServiceImage incluye org:
```python
nas_url = f"{FTP_PATH}/{org_slug}/{service_folder}"
```

**Verificación:** Enviar foto al bot, verificar que se sube a `{FTP_PATH}/{org_slug}/...`

---

## Fase 9 — Panel super-admin para gestión de organizaciones

**Objetivo:** Vista web protegida por `is_superuser` para CRUD de organizaciones y asignación de usuarios.

**Archivos a crear:**
```
organization/
├── views.py
├── urls.py
├── forms.py
└── templates/
    ├── org_list.html
    ├── org_create.html
    └── org_detail.html
```

**Agregar a `common/views.py`:**
```python
class SuperAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied("Solo el super-admin puede acceder.")
        return super().dispatch(request, *args, **kwargs)
```

**Funcionalidades del panel:**
- `GET /organizations/` — listar organizaciones + estado
- `GET /organizations/create/` — formulario crear org (name, slug auto-generado)
- `GET /organizations/<slug>/` — detalle: miembros, stats de servicios
- `POST /organizations/<slug>/toggle/` — activar/desactivar org
- `POST /organizations/<slug>/assign-user/` — asignar user existente a la org

**Verificación:** Login con superuser, verificar CRUD completo de organizaciones.
