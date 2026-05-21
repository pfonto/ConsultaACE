# Copilot / Agent Instructions for ConsultaACE

Breve guía operativa para agentes de código (Copilot-style).

- **Modo inicial**: `default_agent` es `plan`. Antes de modificar archivos, propone un plan corto y explícito.
- **Permiso para shell**: `bash` está marcado como `ask` en `opencode.json`. Pregunta siempre antes de ejecutar cualquier comando de terminal.
- **No subir secretos**: Las credenciales Oracle viven en `.env` (gitignored). Nunca imprimas ni commits secretos.
- **Cómo ejecutar**:

  - Desarrollo: `uv run reflex run`
  - Producción: `uv run reflex run --prod`
  - Sincronizar deps: `uv sync` (solo cuando `pyproject.toml` o `uv.lock` cambien)

- **Entrada principal**: La app arranca desde [ConsultaACE/ConsultaACE.py](ConsultaACE/ConsultaACE.py). No uses `main.py`.
- **Base de datos**: Requiere Oracle; variables de entorno `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`.
- **Artefactos generados**: Ignora `.web/` y `.states/`.
- **Cambios propuestos**: Si añades tests, linters o CI, indica pasos de integración y no los apliques sin aprobación.

Si necesitas ejecutar comandos, pregunta primero y espera la confirmación del mantenedor o del usuario.
