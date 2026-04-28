# Fase 3 — UserProfile: vincular User ↔ Organization

**Fecha:** 2026-04-28  
**Estado:** COMPLETADA

---

## Objetivo

Vincular cada usuario Django (`auth.User`) a una `Organization` mediante un modelo `UserProfile` (OneToOne). Este vínculo es la base del aislamiento de datos multi-tenant: las fases posteriores (Fase 6, Fase 7) lo usan para inyectar la organización en cada request autenticado.

---

## Qué se implementó

### Modelo `UserProfile`

Agregado en `organization/models.py`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | OneToOneField → `AUTH_USER_MODEL` | Un perfil por usuario (CASCADE) |
| `organization` | ForeignKey → `Organization` | Organización a la que pertenece el usuario (CASCADE) |

- `related_name='profile'` en `user` → permite `request.user.profile.organization`
- `related_name='members'` en `organization` → permite `org.members.all()`

### Admin

`organization/admin.py` actualizado con:
- `UserProfileInline` — inline en el panel de User para asignar/ver organización
- `CustomUserAdmin` — extiende `UserAdmin` con el inline
- `User` des-registrado y re-registrado con `CustomUserAdmin`

### Migración

`organization/migrations/0002_userprofile.py` — crea tabla `organization_userprofile`.

### Tests

`organization/tests.py` creado con 4 tests:
- Creación básica de UserProfile
- Representación `__str__`
- Restricción OneToOne (no puede haber dos perfiles por usuario)
- Cascade delete al eliminar la organización

---

## Archivos modificados

```
organization/
├── models.py           — agregado UserProfile + import django.conf.settings
├── admin.py            — reemplazado completo con CustomUserAdmin + UserProfileInline
├── tests.py            — creado nuevo
└── migrations/
    └── 0002_userprofile.py — creado por makemigrations
```

---

## Qué probar

```bash
# 1. Activar el venv
source .venv/bin/activate

# 2. Verificar que los tests pasan
python manage.py test organization
# Debe mostrar: Ran 4 tests ... OK

# 3. Verificar migraciones aplicadas
python manage.py showmigrations organization
# Debe mostrar:
# [X] 0001_initial
# [X] 0002_userprofile

# 4. Verificar modelo en Django shell
python manage.py shell
>>> from organization.models import Organization, UserProfile
>>> from django.contrib.auth.models import User
>>> org = Organization.objects.create(name="Demo Org", slug="demo")
>>> user = User.objects.create_user(username="demo", password="demo")
>>> profile = UserProfile.objects.create(user=user, organization=org)
>>> str(profile)
# Debe retornar: 'demo — Demo Org'
>>> user.profile.organization.slug
# Debe retornar: 'demo'

# 5. Verificar Django admin
# python manage.py runserver
# /admin/ → Usuarios → editar cualquier usuario
# Debe aparecer el inline "User profile" con campo organización
```

---

## Decisiones relevantes

- `UserProfile` usa `models.Model` (no `CommonBaseModel`) — es un modelo de vínculo, no una entidad de negocio con auditoría.
- `on_delete=models.CASCADE` en ambas FK — si se borra el usuario o la org, el perfil se borra también. Sin huérfanos.

---

## Siguiente fase

[Fase 4 — FK `organization` en Employee, Client, Service](./implementation-plan.md#fase-4----fk-organization-en-employee-client-service)
