# Arquitectura

## Estado actual (single-tenant)

```
┌─────────────────────────────────────────────────────────┐
│                    symt-services                        │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐   │
│  │ Web UI   │   │ REST API │   │  Telegram Bot    │   │
│  │(templates│   │  (DRF)   │   │  (PhotosBot.py)  │   │
│  │+Bootstrap│   │          │   │                  │   │
│  └────┬─────┘   └────┬─────┘   └────────┬─────────┘   │
│       │              │                  │              │
│       └──────────────┼──────────────────┘              │
│                      │                                 │
│              ┌───────▼────────┐                        │
│              │   Django ORM   │                        │
│              │ (fat views,    │                        │
│              │  sin capa de   │                        │
│              │  servicio)     │                        │
│              └───────┬────────┘                        │
│                      │                                 │
│              ┌───────▼────────┐   ┌──────────────┐    │
│              │  PostgreSQL    │   │   FTP/NAS    │    │
│              │  (sin org      │   │  (path plano)│    │
│              │   isolation)   │   └──────────────┘    │
│              └────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

### Problemas del estado actual
- `Service.objects.all()` retorna servicios de todos los "clientes"
- `service_number` único globalmente (rompe cuando hay múltiples orgs)
- Lógica de negocio dispersa en views (fat views)
- Bot usa credenciales globales sin contexto de org

---

## Estado objetivo (SaaS multi-tenant)

```
┌─────────────────────────────────────────────────────────────────┐
│                         symt-services                           │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌────────────────────────────┐ │
│  │ Web UI   │   │ REST API │   │  Telegram Bot (central)    │ │
│  │(per-org  │   │  (DRF)   │   │  detecta org via chat_id   │ │
│  │ scoped)  │   │          │   │                            │ │
│  └────┬─────┘   └────┬─────┘   └────────────┬───────────────┘ │
│       │              │                       │                  │
│       └──────────────┼───────────────────────┘                  │
│                      │                                          │
│              ┌───────▼──────────────────────────┐               │
│              │         Service Layer             │               │
│              │  selectors.py  │  services.py     │               │
│              │  (read, org-   │  (write, biz     │               │
│              │   filtered)    │   logic)         │               │
│              └───────┬──────────────────────────┘               │
│                      │                                          │
│              ┌───────▼────────┐   ┌──────────────────────────┐ │
│              │  Django Models │   │   FTP/NAS                │ │
│              │  + Organization│   │  /{org_slug}/            │ │
│              │    FK everywhere│  │    /{service_folder}/    │ │
│              └───────┬────────┘   └──────────────────────────┘ │
│                      │                                          │
│              ┌───────▼────────┐                                 │
│              │  PostgreSQL    │                                  │
│              │  (shared DB,   │                                  │
│              │  org isolation │                                  │
│              │  via FK)       │                                  │
│              └────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Modelo de datos objetivo

```
Organization
  ├── id
  ├── name
  ├── slug (unique)
  └── is_active

UserProfile
  ├── user (OneToOne → User)
  └── organization (FK → Organization)

Employee
  ├── organization (FK → Organization)  ← NUEVO
  ├── first_name, last_name
  ├── phone_number, chat_id
  └── is_active

Client
  ├── organization (FK → Organization)  ← NUEVO
  ├── first_name, company, phone_number
  ├── responsible, is_active
  └── address (FK → Address)

Service
  ├── organization (FK → Organization)  ← NUEVO
  ├── service_number  [unique_together con organization]  ← CAMBIA
  ├── client (FK → Client)
  ├── employee (FK → Employee)
  ├── service_title, description, summary
  ├── status, assigment_date, end_date
  └── images → ServiceImage[]

ServiceImage
  ├── service (FK → Service)
  ├── image (ImageField)
  └── nas_url  [incluye org_slug en el path]  ← CAMBIA
```

---

## Capas de la aplicación

| Capa | Responsabilidad | Archivos |
|------|----------------|---------|
| Models | Definición de datos, sin lógica | `*/models.py` |
| Selectors | Queries a BD, filtradas por org | `*/selectors.py` |
| Services | Lógica de negocio, mutaciones | `*/services.py` |
| Views (web) | HTTP in/out, delgadas | `*/views.py` |
| API Views | HTTP in/out para bot, delgadas | `apis/*/views.py` |
| Bot | Interfaz Telegram, llama API interna | `PhotosBot.py` |

---

## Stack tecnológico

- **Backend:** Django 5.1.6 + Python 3.12
- **API:** Django REST Framework + JWT (rest_framework_simplejwt)
- **DB:** PostgreSQL (producción) / SQLite (desarrollo)
- **Bot:** python-telegram-bot 21.10
- **Archivos:** FTP/NAS + Django ImageField (MEDIA_ROOT)
- **PDF:** WeasyPrint
- **Frontend:** Django Templates + Bootstrap 5 + ApexCharts
