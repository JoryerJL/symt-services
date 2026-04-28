# Changelog — Fases SaaS completadas

Registro de qué se implementó en cada fase y qué verificar antes de continuar a la siguiente.

---

## Fase 5 — Selectors + Service Layer

**Fecha:** 2026-04-28
**Rama:** `feat/fase-5-selectors-service-layer`

### Qué se implementó

- 6 archivos nuevos: `selectors.py` y `services.py` en service, employee y client
- `AdminRequiredMixin` ahora inyecta `request.organization` en cada request
- Todas las views usan selectors/services — sin queries ORM directas
- `generate_report_view` convertida a `GenerateReportView` (CBV con org-scoping)
- `change_employee_status` y `change_client_status` convertidas a CBVs
- 25 tests nuevos (40 totales, todos pasan)

### Qué probar

```bash
source .venv/bin/activate
python manage.py test service employee client organization
# → Ran 40 tests ... OK
```

---

## Fase 4 — FK `organization` en Employee, Client, Service

**Fecha:** 2026-04-28  
**Rama:** `feat/fase-4-organization-fk`

### Qué se implementó

- FK `organization` (null=True) en `Employee`, `Client`, `Service`
- `Service.service_number`: eliminado `unique=True` global → `unique_together = ('organization', 'service_number')`
- Admins actualizados: `list_display` y `list_filter` con `organization` en los 3 modelos
- 3 migraciones generadas y aplicadas: `0004`, `0007`, `0010`
- 11 tests nuevos en `employee/tests.py`, `client/tests.py`, `service/tests.py` (15 totales, todos pasan)

### Archivos creados/modificados

```
employee/models.py                              — FK organization
employee/admin.py                               — list_display/list_filter
employee/tests.py                               — 3 tests nuevos
employee/migrations/0004_employee_organization.py

client/models.py                                — FK organization
client/admin.py                                 — list_display/list_filter
client/tests.py                                 — 3 tests nuevos
client/migrations/0007_client_organization.py

service/models.py                               — FK organization + unique_together
service/admin.py                                — list_display/list_filter
service/tests.py                                — 5 tests nuevos
service/migrations/0010_alter_service_options_service_organization_and_more.py
```

### Qué probar

```bash
PYTHONPATH=.venv/lib/python3.12/site-packages \
  /Users/joryerjimenez/.local/share/uv/python/cpython-3.12.12-macos-aarch64-none/bin/python3.12 \
  manage.py test employee.tests client.tests service.tests organization.tests
# → Ran 15 tests ... OK
```

---

## Fase 3 — UserProfile: vincular User ↔ Organization

**Fecha:** 2026-04-28  
**Rama:** `develop`

### Qué se implementó

- Modelo `UserProfile` en `organization/models.py`:
  - `user` — OneToOneField → `AUTH_USER_MODEL` (related_name `profile`)
  - `organization` — ForeignKey → `Organization` (related_name `members`)
  - `__str__` retorna `"username — org_name"`
- `organization/admin.py` actualizado: `UserProfileInline` inyectado en `CustomUserAdmin`
- Migración `0002_userprofile` generada y aplicada
- Tests creados en `organization/tests.py` (4 tests, todos pasan)

### Archivos creados/modificados

```
organization/models.py                      — UserProfile agregado
organization/admin.py                       — CustomUserAdmin + UserProfileInline
organization/tests.py                       — creado nuevo (4 tests)
organization/migrations/0002_userprofile.py — migración nueva
```

### Qué probar

```bash
source .venv/bin/activate

# Tests
python manage.py test organization
# → Ran 4 tests ... OK

# Admin
python manage.py runserver
# /admin/ → Usuarios → editar user → ver inline "User profile"
```

---

## Fase 2 — App `organization`: modelo + migraciones

**Fecha:** 2026-04-28  
**Rama:** `feat/fase-2-organization-model`

### Qué se implementó

- Nueva Django app `organization/` con el modelo `Organization(CommonBaseModel)`:
  - `name` — nombre de la empresa cliente
  - `slug` — identificador único usado en FTP paths y API responses
  - `is_active` — permite desactivar sin eliminar
- App registrada en `INSTALLED_APPS` (primera en `LOCAL_APPS`)
- Migración `0001_initial` generada y aplicada
- Modelo registrado en Django admin

### Archivos creados

```
organization/
├── __init__.py
├── apps.py
├── models.py
├── admin.py
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### Archivos modificados

- `BotPhotosSYMT/settings.py` — `'organization'` agregado primero en `LOCAL_APPS`

### Qué probar

```bash
# 1. Activar el venv
source .venv/bin/activate

# 2. Verificar que la migración ya está aplicada
python manage.py showmigrations organization
# Debe mostrar: [X] 0001_initial

# 3. Verificar el modelo en Django shell
python manage.py shell
>>> from organization.models import Organization
>>> Organization._meta.fields
# Debe mostrar: id, created_at, updated_at, name, slug, is_active

# 4. Verificar tabla en DB
python manage.py dbshell
sqlite> .tables
# Debe aparecer: organization_organization

# 5. Verificar Django admin
# Iniciar servidor: python manage.py runserver
# Ir a http://localhost:8000/admin/
# Login con superuser → debe aparecer sección "Organization" con modelo "Organizations"
```

---
