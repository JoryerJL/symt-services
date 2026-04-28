# Fase 7 — API (DRF): ViewSets usan selectors + services

**Fecha:** 2026-04-28
**Rama:** `feat/fase-7-api-drf`

## Objetivo

Cerrar la migración de DRF al patrón HackSoft: los ViewSets del bot dejan de consultar el ORM directamente y pasan a delegar lecturas y escrituras en `selectors.py` y `services.py`, preparando el aislamiento multi-org para el flujo del bot central.

## Qué se implementó

### Employee API

- `apis/employee/views.py`
  - `GET /api/employee/?chat_id=...` ahora usa `employee.selectors.get_employee_by_chat_id`
  - `GET /api/employee/?phone_number=...` ahora usa `employee.selectors.get_employee_by_phone`
  - `PUT /api/employee/<id>/` actualiza `chat_id` vía `employee.services.employee_update_chat_id`
  - ya no existe listado global por queryset abierto; si no se envía `chat_id` o `phone_number`, responde `400`

- `apis/employee/serializers.py`
  - agrega `organization_id`
  - agrega `organization_slug`
  - conserva el contrato que necesita el bot para bootstrap y actualización de `chat_id`

### Service API

- `apis/service/views.py`
  - `GET /api/service/<id>/` ahora usa `service.selectors.get_service_by_pk`
  - `PATCH /api/service/<id>/` mueve el append de `summary` a `service.services.service_update_from_api`
  - deja de depender de un queryset global abierto para el flujo actual del bot

### Client API

- `apis/client/views.py`
  - `GET /api/client/<id>/` ahora usa `client.selectors.get_client_by_pk`
  - `GET /api/client/` queda bloqueado con `400` para evitar exposición global accidental de clientes

## Archivos modificados

| Archivo | Qué cambió |
|---------|------------|
| `apis/employee/views.py` | lookups y update vía selectors/services |
| `apis/employee/serializers.py` | `organization_id` y `organization_slug` read-only |
| `apis/service/views.py` | retrieve por selector, partial update apoyado en service layer |
| `apis/client/views.py` | retrieve por selector, bloqueo de listado global |
| `employee/selectors.py` | nuevo `get_employee_by_pk` |
| `service/selectors.py` | nuevo `get_service_by_pk` |
| `service/services.py` | nuevo `service_update_from_api` |
| `client/selectors.py` | nuevo `get_client_by_pk` |
| `apis/tests.py` | tests DRF para employee, service y client |
| `docs/implementation-plan.md` | checkbox de Fase 7 marcado |
| `docs/changelog.md` | entrada de Fase 7 agregada |
| `docs/README.md` | índice actualizado |

## Qué probar

```bash
source .venv/bin/activate

# Tests de la fase
python manage.py test apis employee client service

# Verificación manual del contrato usado por el bot
python manage.py runserver

# En otra terminal:
curl "http://localhost:8000/api/employee/?chat_id=123"
curl "http://localhost:8000/api/employee/?phone_number=5551234567"
curl "http://localhost:8000/api/service/1/"
```

## Decisiones relevantes

- **D-002:** `GET /api/employee/?chat_id=X` sigue siendo una búsqueda GLOBAL porque ese endpoint hace el bootstrap de autenticación del bot.
- **D-004:** los ViewSets DRF también deben ser delgados; la lógica de acceso a datos y mutaciones vive en selectors/services.

## Siguiente fase

[Fase 8 — Bot central multi-org](./implementation-plan.md#fase-8--bot-central-multi-org)
