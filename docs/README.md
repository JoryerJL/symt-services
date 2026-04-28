# symt-services — Documentación

Este directorio contiene la documentación técnica del proyecto para que cualquier agente o desarrollador pueda retomar el trabajo desde donde se quedó.

## Índice

| Archivo | Contenido |
|---------|-----------|
| [implementation-plan.md](./implementation-plan.md) | Plan maestro de implementación SaaS con fases y estado actual |
| [architecture.md](./architecture.md) | Arquitectura actual vs objetivo (diagrama + descripción) |
| [decisions.md](./decisions.md) | Decisiones técnicas tomadas con su justificación |
| [changelog.md](./changelog.md) | Qué se implementó en cada fase y qué probar |

### Documentación por fase

| Archivo | Fase |
|---------|------|
| [fase-2-organization.md](./fase-2-organization.md) | Fase 2 — App `organization`: modelo + migraciones |

## ¿Cómo usar estos docs?

1. **Si eres un agente nuevo:** Lee `implementation-plan.md` primero. Tiene el estado de cada fase con checkboxes. Busca la primera fase sin completar y continúa desde ahí.
2. **Si tienes dudas de diseño:** Lee `decisions.md` antes de proponer cambios. Las decisiones ya tomadas no deben re-debatirse sin contexto.
3. **Si cambias la arquitectura:** Actualiza `architecture.md` para reflejar el estado actual real.

## Regla de oro

Cuando termines una fase, marca su checkbox en `implementation-plan.md` y anota cualquier decisión nueva en `decisions.md`.
