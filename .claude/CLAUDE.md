# symt-services — Instrucciones del proyecto

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

## Plan maestro

El plan está en `docs/implementation-plan.md`. Lee los checkboxes y trabaja siempre desde la primera fase incompleta hacia adelante.

Antes de iniciar cualquier fase, lee `docs/decisions.md` — las decisiones de arquitectura ya están tomadas y no deben re-debatirse.
