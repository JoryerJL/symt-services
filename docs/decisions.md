# Decisiones Técnicas

Este archivo registra las decisiones de diseño tomadas para la conversión a SaaS. Cada decisión incluye el razonamiento para que pueda ser evaluada en contexto futuro.

---

## D-001: Estrategia de multi-tenancy — Shared DB con FK `organization`

**Decisión:** Una sola base de datos, con un campo `organization` (ForeignKey) en cada tabla de negocio (Employee, Client, Service).

**Alternativas consideradas:**
- Separate DB per tenant — demasiado overhead operacional para esta escala
- Separate schema per tenant (PostgreSQL) — complejidad de migrations, no estándar en Django
- Shared DB con row-level security — requiere configuración externa a Django ORM

**Por qué shared DB:** Es el enfoque más simple y el más compatible con Django ORM. Las queries se filtran siempre por `organization`, garantizando el aislamiento a nivel de aplicación.

**Riesgo conocido:** Si una query olvida el filtro `organization`, puede haber data leak. Se mitiga con el patrón Selectors (D-004).

---

## D-002: Bot de Telegram — Un bot central

**Decisión:** Un solo bot de Telegram (un TOKEN). Detecta la organización del empleado via lookup por `chat_id` en el primer contacto.

**Alternativas consideradas:**
- Un bot por organización (tokens separados) — cada org registra su propio bot

**Por qué bot central:** Operativamente más simple. Una sola instancia corriendo. El aislamiento se logra filtrando por `employee.organization` después del bootstrap de auth.

**Implicación:** El endpoint `GET /api/employee/?chat_id=X` es una búsqueda global (no filtrada por org) porque es el paso de autenticación inicial del bot. Todos los demás endpoints filtran por org.

---

## D-003: Creación de organizaciones — Solo super-admin

**Decisión:** No hay auto-registro. Solo un superusuario Django puede crear organizaciones.

**Por qué:** El modelo de negocio es B2B controlado. El dueño del sistema decide qué empresas tienen acceso.

---

## D-004: Capa de acceso a datos — Selectors + Service Layer (HackSoft pattern)

**Decisión:** Se implementa el patrón de HackSoft Django Styleguide:
- `selectors.py` por app: funciones puras que LEEN de la BD
- `services.py` por app: funciones puras que ESCRIBEN en la BD (lógica de negocio)
- Las views son delgadas: solo llaman selectors o services, nunca hacen queries directas

**Referencia:** https://github.com/HackSoftware/Django-Styleguide

**Por qué:** Evita que la lógica de negocio se duplique entre views, API viewsets y el bot. Todos llaman los mismos services. Además, los selectors son la capa que garantiza que siempre se filtre por `organization`, haciendo el data leak difícil de cometer por error.

---

## D-005: Modelo Organization — Solo name + slug + is_active

**Decisión:** El modelo Organization tiene campos mínimos: `name`, `slug` (único, para FTP path), `is_active`.

**Campos descartados para MVP:**
- Token bot Telegram propio — se usa bot central (ver D-002)
- Config FTP propia — todas las orgs comparten el mismo servidor FTP, separadas por subdirectorio
- Plan/suscripción — fuera del alcance del MVP

---

## D-006: Estructura FTP por organización

**Decisión:** Las fotos de cada organización van en un subdirectorio con su `slug`:

```
{FTP_PATH}/
├── {org_slug}/
│   ├── {service_number}-{client}-{date}/
│   │   ├── imagen1.jpg
│   │   └── imagen2.jpg
```

**Por qué slug y no ID:** El slug es legible y no cambia. Facilita auditorías manuales del FTP.

---

## D-007: service_number — Secuencial por organización

**Decisión:** `service_number` es único por organización (`unique_together = ('organization', 'service_number')`), no globalmente único.

**Implementación:** Al crear un servicio, se hace `MAX(service_number) + 1` filtrado por org. La lógica vive en `service/services.py::service_create`.

**Implicación de migración:** El campo `unique=True` existente debe eliminarse y reemplazarse por `unique_together`. Los datos existentes deben asignarse a una organización antes de aplicar la constraint.

---

## D-008: UserProfile — Vinculación User ↔ Organization

**Decisión:** Se usa un modelo `UserProfile` con `OneToOneField` al `User` de Django, que tiene un `ForeignKey` a `Organization`.

**Por qué no extender User:** `OneToOneField` es el patrón Django idiomático. Permite reusar `AUTH_USER_MODEL` sin modificarlo.

**Acceso en views:** `request.user.profile.organization` (expuesto como `request.organization` desde `AdminRequiredMixin`).
