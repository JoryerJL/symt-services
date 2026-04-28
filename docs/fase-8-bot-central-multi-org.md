# Fase 8 — Bot central multi-org

**Fecha:** 2026-04-28
**Rama:** `feat/fase-8-bot-central-multi-org`

## Objetivo

Hacer que el bot central preserve el contexto de organización durante todo el flujo operativo: confirmación, subida de fotos, guardado de `nas_url` y finalización del servicio.

## Qué se implementó

### Contexto activo por chat

- `PhotosBot.py`
  - `active_service[chat_id]` dejó de ser un `str`
  - ahora guarda:
    - `service_id`
    - `service_number`
    - `org_slug`
    - `folder`

### Aislamiento FTP por organización

- `verify_or_create_ftp_folder(org_slug, folder_name)`
  - garantiza que exista la carpeta de organización antes de crear la carpeta del servicio

- `upload_a_ftp(local_name, org_slug, remote_folder, remote_name)`
  - sube archivos a `{FTP_PATH}/{org_slug}/{service_folder}`

### Identidad correcta del servicio

- el bot ya NO usa `service_number` para consultar `GET /api/service/<id>/` ni para finalizar servicios
- ahora usa `service_id`, que sí es único globalmente
- esto evita colisiones entre organizaciones donde `service_number=1` puede existir más de una vez

### NAS URL multi-org

- `ServiceImage.nas_url` ahora se guarda con el prefijo de organización:
  - `{FTP_PATH}/{org_slug}/{service_folder}`

## Archivos modificados

| Archivo | Qué cambió |
|---------|------------|
| `PhotosBot.py` | estado multi-org por chat, lookup por `service_id`, FTP y `nas_url` con `org_slug` |
| `service/test_photos_bot.py` | tests del flujo multi-org del bot y helpers FTP |
| `docs/implementation-plan.md` | checkbox de Fase 8 marcado |
| `docs/decisions.md` | decisión D-009 agregada |
| `docs/changelog.md` | entrada de Fase 8 agregada |
| `docs/README.md` | índice actualizado |

## Qué probar

```bash
source .venv/bin/activate

# Suite relevante de la fase
python manage.py test service.test_photos_bot apis service

# Flujo manual
python manage.py runserver
python PhotosBot.py
```

### Pasos manuales exactos

1. En Telegram, confirma un servicio desde el botón enviado al empleado.
2. Sube una foto al servicio activo.
3. Finaliza el servicio y envía un resumen.
4. Verifica que:
   - la API no falló al consultar/finalizar el servicio
   - el archivo quedó en `{FTP_PATH}/{org_slug}/{service_number}-{cliente}-{fecha}/`
   - `ServiceImage.nas_url` incluye `org_slug`

## Decisiones relevantes

- **D-002:** sigue existiendo un solo bot central; el aislamiento se logra después del bootstrap del empleado.
- **D-007:** `service_number` es único por organización, no globalmente.
- **D-009:** el estado del bot debe guardar `service_id` y `org_slug` para evitar mezclar tenants.

## Siguiente fase

[Fase 9 — Panel super-admin para gestión de organizaciones](./implementation-plan.md#fase-9--panel-super-admin-para-gestión-de-organizaciones)
