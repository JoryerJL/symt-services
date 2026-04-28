# symt-services — Instrucciones del proyecto

## Regla: Inicio de cada fase SaaS

Antes de implementar cualquier fase, DEBES crear una rama nueva desde `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/fase-{N}-{nombre-corto}
```

Trabaja SIEMPRE en esa rama. Nunca commitees cambios de una fase directamente en `develop`.

## Regla: Fin de cada fase SaaS

Al terminar cualquier fase del plan SaaS (`docs/implementation-plan.md`), DEBES hacer lo siguiente antes de reportar "listo":

1. **Marcar el checkbox** de la fase en `docs/implementation-plan.md`.
2. **Crear el archivo de fase** `docs/fase-{N}-{nombre}.md` con:
   - Objetivo de la fase
   - Qué se implementó (modelos, campos, archivos, cambios)
   - Tabla de campos si hay modelos nuevos
   - Qué probar (pasos exactos con comandos)
   - Decisiones relevantes (referencias a `decisions.md`)
   - Enlace a la siguiente fase
3. **Agregar una entrada** en `docs/changelog.md` con resumen + pasos de prueba.
4. **Actualizar el índice** `docs/README.md` con el nuevo archivo de fase.
5. **Decirle al usuario** explícitamente qué probar, con los comandos exactos.

No reportes la fase como terminada sin completar estos cinco pasos.

## Regla: Commits atómicos

Cada commit debe tener UNA sola responsabilidad. Nunca agrupes cambios de distinta naturaleza en un commit.

Orden recomendado dentro de una fase:

1. **Tests** — `test: add X tests for Y`
2. **Modelos** — `feat: add organization FK to Employee` (uno por modelo si son independientes)
3. **Migraciones** — `chore: add migration for organization FK in Employee`
4. **Admin** — `feat: update Employee admin with organization filter`
5. **Docs** — `docs: add fase-N doc and update changelog`

Reglas:
- Un commit por modelo si los cambios son independientes entre sí.
- Tests y su implementación van en commits SEPARADOS (RED primero, GREEN después).
- Nunca mezcles modelos + migraciones + admin + docs en un solo commit.
- Si dudas si algo merece su propio commit: sí merece.

## Plan maestro

El plan está en `docs/implementation-plan.md`. Lee los checkboxes y trabaja siempre desde la primera fase incompleta hacia adelante.

Antes de iniciar cualquier fase, lee `docs/decisions.md` — las decisiones de arquitectura ya están tomadas y no deben re-debatirse.
