# Skill: agent-setup

Objetivo: proporcionar pasos rápidos y repetibles para que un agente prepare el entorno de desarrollo local y ejecute tareas comunes de onboarding.

Uso previsto por agentes automatizados:

1. **Comprobar entorno**
   - Verificar que `.venv/` existe y que el entorno está activado.
   - Si no está activado, indicar al usuario el comando para activarlo.

2. **Sincronizar dependencias**
   - Ejecutar `uv sync` solo si `pyproject.toml` o `uv.lock` han cambiado — pedir confirmación antes.

3. **Variables sensibles**
   - Recordar usar `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`. No sugerir valores reales.

4. **Arrancar la app**
   - Desarrollo: `uv run reflex run`
   - Producción (build): `uv run reflex run --prod`

5. **Comprobaciones básicas**
   - Confirmar que `ConsultaACE/ConsultaACE.py` existe.
   - Revisar `ConsultaACE/db.py` para las variables `ORACLE_*`.

Comportamiento requerido:

- Siempre generar un pequeño checklist antes de ejecutar comandos reales.
- No ejecutar `uv sync` ni comandos de despliegue sin permiso humano.
- En caso de falta de acceso a la base de datos, explicar que la app fallará y proponer pasos alternativos (mocks, pruebas unitarias aisladas).
