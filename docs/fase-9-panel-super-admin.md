# Fase 9 — Panel super-admin para gestión de organizaciones

**Fecha:** 2026-04-28
**Rama:** `feat/fase-9-panel-super-admin`

## Objetivo

Agregar un panel web exclusivo para `is_superuser` que permita administrar organizaciones del SaaS: listarlas, crearlas, editarlas, ver su detalle operativo, activar/desactivar y asignar usuarios existentes sin organización.

## Qué se implementó

### Protección por superusuario

- `common/views.py`
  - nuevo `SuperAdminRequiredMixin`
  - permite acceso solo a usuarios autenticados con `is_superuser=True`

### Panel de organizaciones

- `organization/views.py`
  - `OrganizationListView` para listar organizaciones con conteos rápidos
  - `OrganizationCreateView` para crear organizaciones con slug auto-generado
  - `OrganizationDetailView` para mostrar miembros y resumen operativo
  - `OrganizationUpdateView` para editar el nombre sin cambiar el slug
  - `OrganizationToggleView` para activar/desactivar
  - `OrganizationAssignUserView` para asignar usuarios existentes

- `organization/urls.py`
  - nuevas rutas bajo `/organizations/`

- `BotPhotosSYMT/urls.py`
  - inclusión del módulo `organization.urls`

### Formularios, lectura y escritura

- `organization/forms.py`
  - formulario de creación de organización
  - formulario de edición de organización
  - formulario de asignación de usuario

- `organization/selectors.py`
  - lecturas del panel: listado, detalle, miembros y stats

- `organization/services.py`
  - creación de organización con slug único
  - edición del nombre conservando el slug
  - toggle de `is_active`
  - asignación de usuario con bloqueo si ya pertenece a otra organización

### Navegación y templates

- `templates/sidebar.html`
  - enlace a Organizaciones visible solo para superusuarios

- `organization/templates/`
  - `org_list.html`
  - `org_create.html`
  - `org_edit.html`
  - `org_detail.html`

## Tabla de campos

No se agregaron campos nuevos ni migraciones en esta fase.

## Qué probar

```bash
source .venv/bin/activate

# Suite relevante de la fase
python manage.py test organization employee client service apis

# Verificación manual
python manage.py runserver
```

### Pasos manuales exactos

1. Inicia sesión con un superusuario.
2. Entra a `http://localhost:8000/organizations/`.
3. Verifica que se muestren organizaciones con estado y conteos.
4. Crea una organización nueva desde `http://localhost:8000/organizations/create/`.
5. Edita la organización creada desde su listado o detalle y confirma que:
   - cambia el nombre
   - el `slug` NO cambia
6. Abre el detalle de la organización creada y confirma que se vean:
   - slug
   - miembros
   - total de servicios
   - activos/asignados
   - finalizados
   - empleados
   - clientes
7. Usa el botón de activar/desactivar y confirma que cambie el estado.
8. Asigna un usuario existente SIN organización y confirma que se crea su `UserProfile`.
9. Intenta asignar un usuario que ya pertenece a otra organización y confirma que la operación se rechaza.

## Decisiones relevantes

- **D-003:** solo el super-admin puede crear organizaciones.
- **D-008:** la vinculación usuario ↔ organización sigue viviendo en `UserProfile`.
- **D-010:** desde este panel solo se asignan usuarios sin organización; no hay reasignación entre tenants en esta fase.

## Siguiente fase

Plan maestro completado hasta la Fase 9 actual.
