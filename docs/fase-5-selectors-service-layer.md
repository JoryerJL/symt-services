# Fase 5 — Selectors + Service Layer

**Fecha:** 2026-04-28
**Rama:** `feat/fase-5-selectors-service-layer`

## Objetivo

Introducir el patrón HackSoft (D-004): funciones puras que concentran toda la lógica de acceso a datos y lógica de negocio. Las views se vuelven delgadas — solo validan formularios, llaman un selector o service, y redireccionan.

## Qué se implementó

### Archivos nuevos

| Archivo | Funciones |
|---------|-----------|
| `service/selectors.py` | `get_services_for_org`, `get_service_by_id`, `get_active_services`, `get_services_by_status` |
| `service/services.py` | `service_create`, `service_assign_employee`, `service_finalize`, `service_reactivate` |
| `employee/selectors.py` | `get_employee_by_chat_id`, `get_employee_by_phone`, `get_employees_for_org` |
| `employee/services.py` | `employee_update_chat_id`, `employee_toggle_status` |
| `client/selectors.py` | `get_clients_for_org`, `get_client_by_id` |
| `client/services.py` | `client_create`, `client_toggle_status` |

### Archivos modificados

| Archivo | Qué cambió |
|---------|------------|
| `common/views.py` | `AdminRequiredMixin` ahora inyecta `request.organization` (desde `request.user.profile.organization`) |
| `service/views.py` | Todas las views usan selectors/services. `generate_report_view` convertida a `GenerateReportView` (CBV) |
| `service/urls.py` | Actualizado para usar `ReactivateServiceView` y `GenerateReportView` |
| `employee/views.py` | `change_employee_status` convertida a `ChangeEmployeeStatusView` (CBV) |
| `employee/urls.py` | Actualizado para usar `ChangeEmployeeStatusView` |
| `client/views.py` | `change_client_status` convertida a `ChangeClientStatusView` (CBV) |
| `client/urls.py` | Actualizado para usar `ChangeClientStatusView` |

### Tests agregados (25 nuevos, 40 totales)

- `service/tests.py` — `ServiceSelectorsTest` (5 tests), `ServiceServicesTest` (8 tests)
- `employee/tests.py` — `EmployeeSelectorsTest` (3 tests), `EmployeeServicesTest` (3 tests)
- `client/tests.py` — `ClientSelectorsTest` (3 tests), `ClientServicesTest` (3 tests)

## Decisiones tomadas en esta fase

- **Telegram en service layer:** `service_create` y `service_assign_employee` llaman `send_msg` y `send_confirm_msg` internamente. Las views no saben de Telegram.
- **Assigned vs Reassigned:** `service_assign_employee` detecta si el servicio ya tenía empleado (`had_employee`) y asigna el status correcto.
- **Forms siguen para validación HTTP:** `form.save()` eliminado. Las views llaman `form.is_valid()` y luego el service con `form.cleaned_data`.
- **`generate_report_view` convertida a CBV:** Era la única vista function-based sin auth. Ahora `GenerateReportView(AdminRequiredMixin, View)` garantiza org-scoping.

## Qué probar

```bash
source .venv/bin/activate

# Tests
python manage.py test service employee client organization
# → Ran 40 tests ... OK

# Verificar aislamiento (manual)
# 1. Crear dos organizaciones (Org A, Org B) en /admin/
# 2. Crear dos usuarios, asignar uno a cada org via UserProfile
# 3. Login con usuario Org A → /services/ → solo debe ver servicios de Org A
# 4. Login con usuario Org B → /services/ → solo debe ver servicios de Org B
```

## Siguiente fase

[Fase 6 — Vistas web: delgadas, usan selectors + services](./implementation-plan.md#fase-6)
