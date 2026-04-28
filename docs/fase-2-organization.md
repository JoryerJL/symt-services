# Fase 2 — App `organization`: modelo + migraciones

**Estado:** COMPLETADA  
**Fecha:** 2026-04-28  
**Rama:** `feat/fase-2-organization-model`  
**Commits:**
- `5561c42` — feat: add organization app with Organization model and migration
- `1f4979c` — docs: add fase 2 changelog and phase completion rule

---

## Objetivo

Crear la Django app `organization` con el modelo `Organization` como base del sistema multi-tenant. Sin este modelo no pueden existir las fases 3-9 — es la piedra angular del aislamiento por organización.

---

## Qué se implementó

### Modelo `Organization`

```python
# organization/models.py
class Organization(CommonBaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
```

**Hereda de `CommonBaseModel`** (`common/models.py`), que agrega:
- `created_at` — `DateTimeField(auto_now_add=True)`
- `updated_at` — `DateTimeField(auto_now=True)`
- `Meta.ordering = ["-created_at"]`

**Campos propios:**

| Campo | Tipo | Restricción | Uso |
|-------|------|-------------|-----|
| `name` | `CharField(150)` | — | Nombre de la empresa cliente |
| `slug` | `SlugField` | `unique=True` | Identificador en FTP paths y API responses |
| `is_active` | `BooleanField` | `default=True` | Desactivar org sin eliminarla (Fase 9) |

**Por qué `slug` y no `id` para FTP:** El slug es legible y no cambia. `acme-corp/123-ClienteX-2025-01-01` es auditable manualmente. Ver D-006 en `decisions.md`.

### Estructura de archivos creada

```
organization/
├── __init__.py
├── apps.py              ← OrganizationConfig, default_auto_field = BigAutoField
├── models.py            ← Organization(CommonBaseModel)
├── admin.py             ← admin.site.register(Organization) básico
└── migrations/
    ├── __init__.py
    └── 0001_initial.py  ← crea tabla organization_organization
```

### Modificación en `settings.py`

`'organization'` se colocó **primero** en `LOCAL_APPS`:

```python
LOCAL_APPS = [
    'organization',   # ← primero: las demás apps dependerán de ella vía FK
    'service',
    'common',
    'employee',
    'client',
]
```

**Por qué primero:** En Fases 3-4, `service`, `employee` y `client` agregarán `ForeignKey` a `Organization`. Django resuelve dependencias de migrations en el orden de `INSTALLED_APPS` — ponerla primero evita problemas de orden de migración.

---

## Tabla en base de datos

Tabla generada: `organization_organization`

| Columna | Tipo SQLite | Notas |
|---------|-------------|-------|
| `id` | `INTEGER` | PK autoincremental |
| `created_at` | `DATETIME` | auto_now_add |
| `updated_at` | `DATETIME` | auto_now |
| `name` | `VARCHAR(150)` | |
| `slug` | `VARCHAR(50)` | `UNIQUE` |
| `is_active` | `BOOL` | default 1 |

---

## Qué probar

```bash
source .venv/bin/activate

# 1. Migración aplicada correctamente
python manage.py showmigrations organization
# [X] 0001_initial

# 2. Campos del modelo
python manage.py shell -c "
from organization.models import Organization
print([f.name for f in Organization._meta.fields])
"
# ['id', 'created_at', 'updated_at', 'name', 'slug', 'is_active']

# 3. Tabla existe en SQLite
python manage.py dbshell
sqlite> .tables
# ... organization_organization ...
sqlite> .schema organization_organization
# Verificar columnas y constraints

# 4. CRUD básico desde shell
python manage.py shell -c "
from organization.models import Organization
org = Organization.objects.create(name='Empresa Demo', slug='empresa-demo')
print(org)           # 'Empresa Demo'
print(org.is_active) # True
print(org.created_at)
Organization.objects.filter(slug='empresa-demo').delete()
"

# 5. Django admin
python manage.py runserver
# http://localhost:8000/admin/
# → sección 'ORGANIZATION' con modelo 'Organizations'
# → crear una organización desde el admin y verificar que se guarda
```

---

## Decisiones relevantes

- **D-001** — Shared DB con FK `organization` (esta app es la base de esa estrategia)
- **D-005** — Campos mínimos para MVP: solo `name`, `slug`, `is_active`
- **D-006** — FTP usa `slug` como subdirectorio de la org

Ver `docs/decisions.md` para el razonamiento completo.

---

## Siguiente fase

**Fase 3 — UserProfile:** vincular `User ↔ Organization` con un `OneToOneField`.  
Agrega `UserProfile` en `organization/models.py` y un inline en el admin para asignar org al crear usuarios.
