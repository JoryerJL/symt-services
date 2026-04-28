# Changelog — Fases SaaS completadas

Registro de qué se implementó en cada fase y qué verificar antes de continuar a la siguiente.

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
