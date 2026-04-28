# Fase 6 — Vistas web: delgadas, usan selectors + services

**Fecha:** 2026-04-28
**Rama:** `develop`

## Objetivo

Cerrar la migración de las vistas web al patrón HackSoft: las views coordinan HTTP, pero no hacen queries ORM directas ni ejecutan escrituras de dominio.

## Qué se implementó

### Employee

- `employee/views.py`
  - creación movida a `employee.services.employee_create`
  - lookup por PK movido a `employee.selectors.get_employee_by_id`

### Client

- `client/views.py`
  - creación de `Address` movida a `client.services.address_create`
  - toggle lookup movido a `client.selectors.get_client_by_id`

## Archivos modificados

| Archivo | Qué cambió |
|---------|------------|
| `employee/selectors.py` | nuevo `get_employee_by_id` |
| `employee/services.py` | nuevo `employee_create` |
| `employee/views.py` | sin ORM directo ni `form.save()` |
| `employee/tests.py` | cobertura para selector y service nuevos |
| `client/services.py` | nuevo `address_create` |
| `client/views.py` | sin `address_form.save()` ni ORM directo |
| `client/tests.py` | cobertura para `address_create` |
| `docs/implementation-plan.md` | checkbox de Fase 6 marcado |
| `docs/changelog.md` | entrada de Fase 6 agregada |

## Qué verificar

```bash
source .venv/bin/activate
python manage.py test employee client
```

## Resultado

Con esto, las vistas web de `service`, `employee` y `client` quedan alineadas con la decisión D-004: selectors para lectura, services para escritura, views delgadas.
