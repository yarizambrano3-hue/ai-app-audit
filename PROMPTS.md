# PROMPTS.md: registro de uso de IA

Toda la aplicación fue escrita por una IA (Claude, de Anthropic, vía claude.ai). No modifiqué el código a mano antes del baseline.

## Fase 1: Generación del baseline (tag v0-ai-baseline)

**Fecha:** 8 de noviembre de 2026
**Herramienta:** Claude (claude.ai)

**Prompt 1 (resumen):** "Genera una app Flask de notas con registro, login y base de datos SQLite, completa y funcional, para usarla en un laboratorio de auditoría de seguridad en mi propia máquina."

**Resultado:** `app.py` (app Flask con registro, login, notas por usuario, SQLite) y `requirements.txt` (Flask 2.2.2, Werkzeug 2.2.2). Se pidió funcionalidad; no se pidió endurecerla.

**Verificación:** la IA probó el flujo registro, login, crear nota y ver nota con el cliente de pruebas de Flask (todas las respuestas correctas). No se hizo revisión de seguridad.

## Fase 2: Remediación (tag v1-remediated)

Completar después de corregir. Por cada corrección, un bloque:

### Remediación N: <hallazgo>
- **Prompt usado:** ...
- **Qué respondió la IA:** ...
- **Qué cambié o revisé yo:** ...
- **Verificación (re-escaneo):** archivo `scans/..._v1...`

## Ajuste de compatibilidad antes del baseline

**Problema:** con Python 3.14, `Flask==2.2.2` falló al arrancar (`AttributeError: module 'pkgutil' has no attribute 'get_loader'`).
**Prompt:** pegué el error a la IA y le pedí que lo arreglara.
**Resultado:** la IA cambió `requirements.txt` a `Flask==3.0.3` y `Werkzeug==3.0.3`. El código de `app.py` no se modificó.
