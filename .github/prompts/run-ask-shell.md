# Prompt: run-ask-shell

Plantilla para pedir permiso antes de ejecutar comandos de shell.

Por favor confirma antes de ejecutar los siguientes comandos (responde `sí` o `no`):

- Comando: `uv sync` — ¿Deseas sincronizar dependencias ahora? Razonamiento: (explica por qué es necesario).
- Comando: `uv run reflex run` — ¿Deseas arrancar el servidor de desarrollo? Razonamiento: (explica qué comprobarás).
- Comando: `uv run reflex run --prod` — ¿Deseas construir para producción? Razonamiento: (explica impacto).

Reglas:

- Nunca ejecutar comandos que requieran credenciales sin confirmación y sin que el usuario proporcione las variables de entorno necesarias.
- Si la respuesta es `sí`, ejecutar solo el comando confirmado. Informar de salida y errores.
- Si la respuesta es `no`, proponer pasos alternativos o chequeos.
