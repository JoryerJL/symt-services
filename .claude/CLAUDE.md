# symt-services — Instrucciones del proyecto

## Regla: Fin de cada fase SaaS

Al terminar cualquier fase del plan SaaS (`docs/implementation-plan.md`), DEBES hacer lo siguiente antes de reportar "listo":

1. **Marcar el checkbox** de la fase en `docs/implementation-plan.md`.
2. **Agregar una entrada** en `docs/changelog.md` con:
   - Qué se implementó
   - Archivos creados/modificados
   - Qué debe probar el usuario (pasos exactos)
3. **Decirle al usuario** explícitamente qué probar, con los comandos o pasos exactos.

No reportes la fase como terminada sin completar estos tres pasos.

## Plan maestro

El plan está en `docs/implementation-plan.md`. Lee los checkboxes y trabaja siempre desde la primera fase incompleta hacia adelante.

Antes de iniciar cualquier fase, lee `docs/decisions.md` — las decisiones de arquitectura ya están tomadas y no deben re-debatirse.
