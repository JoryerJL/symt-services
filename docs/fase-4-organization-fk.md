# Fase 4 — FK `organization` en Employee, Client, Service

**Fecha:** 2026-04-28  
**Estado:** COMPLETADA

---

## Objetivo

Vincular las entidades de negocio (Employee, Client, Service) a una `Organization` mediante Foreign Key. Este paso habilita el filtrado por organización en las Fases 5–9 (selectors, vistas, API, bot).

---

## Qué se implementó

### Modelo `Employee`

Campo agregado en `employee/models.py`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `organization` | ForeignKey → `Organization` | Organización del empleado (null=True, CASCADE) |

- `related_name='employees'` → permite `org.employees.all()`

### Modelo `Client`

Campo agregado en `client/models.py`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `organization` | ForeignKey → `Organization` | Organización del cliente (null=True, CASCADE) |

- `related_name='clients'` → permite `org.clients.all()`

### Modelo `Service`

Dos cambios en `service/models.py`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `organization` | ForeignKey → `Organization` | Organización del servicio (null=True, CASCADE) |

- `related_name='services'` → permite `org.services.all()`
- `service_number`: eliminado `unique=True` global; reemplazado por `unique_together = ('organization', 'service_number')` — un número de servicio puede repetirse entre organizaciones distintas.

### Admin

Actualizados los 3 admins con `list_display` y `list_filter` por `organization`:
- `employee/admin.py`
- `client/admin.py`
- `service/admin.py`

### Migraciones

- `employee/migrations/0004_employee_organization.py`
- `client/migrations/0007_client_organization.py`
- `service/migrations/0010_alter_service_options_service_organization_and_more.py`

### Tests

| Archivo | Tests |
|---------|-------|
| `employee/tests.py` | campo existe, puede pertenecer a org, filtrado por org |
| `client/tests.py` | campo existe, puede pertenecer a org, filtrado por org |
| `service/tests.py` | campo existe, puede pertenecer a org, filtrado, unique_together por org, mismo número en orgs distintas |

Total: 11 tests nuevos. 15 tests totales en verde.

---

## Archivos modificados

```
employee/
├── models.py                       — FK organization agregada
├── admin.py                        — list_display/list_filter con organization
├── tests.py                        — 3 tests nuevos
└── migrations/
    └── 0004_employee_organization.py

client/
├── models.py                       — FK organization agregada
├── admin.py                        — list_display/list_filter con organization
├── tests.py                        — 3 tests nuevos
└── migrations/
    └── 0007_client_organization.py

service/
├── models.py                       — FK organization + unique_together
├── admin.py                        — list_display/list_filter con organization
├── tests.py                        — 5 tests nuevos
└── migrations/
    └── 0010_alter_service_options_service_organization_and_more.py

docs/
├── implementation-plan.md          — Fase 4 marcada como completada
├── fase-4-organization-fk.md      — este archivo
├── changelog.md                    — entrada Fase 4 agregada
└── README.md                       — índice actualizado
```

---

## Decisión: datos existentes

Los registros de Employee, Client y Service existentes quedan con `organization=null`. No hay data migration. La asignación se hará manualmente vía admin una vez que haya organizaciones reales creadas.

---

## Qué probar

```bash
# 1. Correr todos los tests
PYTHONPATH=.venv/lib/python3.12/site-packages \
  /Users/joryerjimenez/.local/share/uv/python/cpython-3.12.12-macos-aarch64-none/bin/python3.12 \
  manage.py test employee.tests client.tests service.tests organization.tests
# Debe mostrar: Ran 15 tests ... OK

# 2. Verificar migraciones
python manage.py showmigrations employee client service
# Debe mostrar los nuevos 0004, 0007, 0010 con [X]

# 3. Verificar en Django shell
python manage.py shell
>>> from employee.models import Employee
>>> Employee._meta.get_field('organization')
# Debe retornar: <django.db.models.fields.related.ForeignKey: organization>

# 4. Verificar admin
# /admin/ → Employees/Clients/Services
# Debe mostrar columna "Organization" y filtro lateral por organización
```

---

## Siguiente fase

[Fase 5 — Selectors + Service Layer](./implementation-plan.md#fase-5----selectors--service-layer)
