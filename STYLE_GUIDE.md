# Style Guide & Coding Standards - Project ConsultaACE

## 1. Filosofía de Desarrollo
- **Enfoque Racional:** El código debe ser explícito, legible y basado en la lógica. Se rechaza la "magia" de frameworks si oscurece el flujo de datos.
- **Crítica Rigurosa:** El agente DEBE señalar errores de lógica, redundancias o ineficiencias en las propuestas del usuario. No se busca complacencia, se busca la verdad técnica.

## 2. Stack Tecnológico
- **Frontend/Backend:** Reflex (Python framework).
- **ORM:** SQLAlchemy para la interacción con Oracle/SQLite.
- **Validación:** Uso estricto de Pydantic para esquemas de datos.
- **Entorno:** WSL2 (Ubuntu) en Windows 11.

## 3. Estándares de Python & Reflex
- **Tipado:** Type hinting obligatorio en todas las funciones y componentes de Reflex.
- **Estructura Reflex:** - Separar la lógica de los `State` de la UI (componentes).
    - Los componentes deben ser modulares y reutilizables.
- **Manejo de Errores:** No usar `try-except` genéricos. Capturar excepciones específicas de SQLAlchemy o de conexión.

## 4. Interacción con la Base de Datos (Oracle)
- **Nomenclatura:** Mantener la correspondencia exacta con `database_schema.md`.
- **Portabilidad:** El código debe permitir el cambio fácil entre la cadena de conexión de producción (Oracle) y la de desarrollo local (SQLite).
- **Rendimiento:** Priorizar el uso de `Dato1`, `Dato2`, `Dato3` de la tabla `Eventos` para filtrado inicial antes de consultar `EventosDetalles`.

## 5. Tono de la Interacción
- Directo, técnico y libre de adornos innecesarios.
- Si una implementación sugerida por el usuario es subóptima, el agente debe argumentar en contra usando fundamentos de ingeniería de software o patrones de diseño.