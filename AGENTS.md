# symt-services — Instrucciones del proyecto para Codex

Estas reglas reflejan y refuerzan lo definido en `.claude/CLAUDE.md` para que Codex actúe con el mismo flujo de trabajo dentro de este repositorio.

## Fuente de verdad

- Considera `.claude/CLAUDE.md` como referencia de origen para este flujo.
- Si en el futuro hay diferencias entre este archivo y `.claude/CLAUDE.md`, primero verifica ambos y manténlos sincronizados.

## Regla: Inicio de cada fase SaaS

Antes de implementar cualquier fase, DEBES crear una rama nueva desde `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/fase-{N}-{nombre-corto}
```

Reglas obligatorias:
- Trabaja SIEMPRE en esa rama.
- Nunca commitees cambios de una fase directamente en `develop`.
- Antes de empezar una fase, revisa `docs/implementation-plan.md` y ubica la primera fase incompleta.
- Antes de empezar una fase, lee `docs/decisions.md`. Las decisiones de arquitectura ya están tomadas y no deben re-debatirse.

## Regla: Fin de cada fase SaaS

Al terminar cualquier fase del plan SaaS (`docs/implementation-plan.md`), DEBES hacer lo siguiente antes de reportar "listo":

1. Marcar el checkbox de la fase en `docs/implementation-plan.md`.
2. Crear el archivo de fase `docs/fase-{N}-{nombre}.md` con:
   - Objetivo de la fase
   - Qué se implementó (modelos, campos, archivos, cambios)
   - Tabla de campos si hay modelos nuevos
   - Qué probar (pasos exactos con comandos)
   - Decisiones relevantes (referencias a `decisions.md`)
   - Enlace a la siguiente fase
3. Agregar una entrada en `docs/changelog.md` con resumen + pasos de prueba.
4. Actualizar el índice `docs/README.md` con el nuevo archivo de fase.
5. Decirle al usuario explícitamente qué probar, con los comandos exactos.

NO reportes una fase como terminada sin completar esos cinco pasos.

## Regla: Commits atómicos

Cada commit debe tener UNA sola responsabilidad. Nunca agrupes cambios de distinta naturaleza en un commit.

Orden recomendado dentro de una fase:

1. `test: add X tests for Y`
2. `feat: add organization FK to Employee`
3. `chore: add migration for organization FK in Employee`
4. `feat: update Employee admin with organization filter`
5. `docs: add fase-N doc and update changelog`

Reglas obligatorias:
- Un commit por modelo si los cambios son independientes entre sí.
- Tests y su implementación van en commits SEPARADOS (RED primero, GREEN después).
- Nunca mezcles modelos + migraciones + admin + docs en un solo commit.
- Si dudas si algo merece su propio commit: sí merece.

## Plan maestro

- El plan está en `docs/implementation-plan.md`.
- Trabaja siempre desde la primera fase incompleta hacia adelante.

## Comportamiento esperado de Codex en este repo

- Antes de afirmar que una fase está lista, verifica que la documentación de cierre esté completa.
- Antes de proponer cambios de arquitectura para una fase, verifica `docs/decisions.md`.
- Si una solicitud entra en conflicto con estas reglas, explica el conflicto y propone una alternativa compatible.
