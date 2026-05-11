# database_schema.md

## Base de Datos de IBM ACE v12 - Esquema Completo

Esta base de datos almacena logs, eventos y configuración de las interfaces (aplicaciones) de IBM ACE.

---

## Tabla: APLICACIONES

**Propósito:** Catálogo de todas las aplicaciones/interfaces de ACE.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDAPP | NUMBER | PK | Identificador numérico único |
| APP | VARCHAR2(50) | UNIQUE | Nombre de la aplicación (ej: "SAP_Invoice") |
| VERSIONACTUAL | VARCHAR2(20) | | Versión actual desplegada |
| DESCAPP | VARCHAR2(255) | | Descripción del propósito de la app |
| DESCDATO1 | VARCHAR2(50) | | Título para el campo DATO1 en EVENTOS |
| DESCDATO2 | VARCHAR2(50) | | Título para el campo DATO2 en EVENTOS |
| DESCDATO3 | VARCHAR2(50) | | Título para el campo DATO3 en EVENTOS |

**Relaciones:**
- Una Aplicación tiene muchos EVENTOS
- Una Aplicación tiene muchas VERSIONES
- Una Aplicación tiene muchos PARAMETROS
- Una Aplicación tiene muchas configuraciones de Correos

---

## Tabla: VERSIONES

**Propósito:** Histórico de versiones de cada aplicación.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDAPP | NUMBER | PK, FK → APLICACIONES | Referencia a la aplicación |
| VERSION | VARCHAR2(20) | PK | Número de versión |
| FECHAHORA | TIMESTAMP | | Cuándo se desplegó (default SYSTIMESTAMP) |
| DESPLEGADOPOR | VARCHAR2(40) | | Quién realizó el despliegue |

---

## Tabla: PARAMETROS

**Propósito:** Configuración de funcionamiento de cada interfaz.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDAPP | NUMBER | PK, FK → APLICACIONES | Referencia a la aplicación |
| PARAMETRO | VARCHAR2(50) | PK | Nombre del parámetro |
| VALOR | VARCHAR2(200) | | Valor del parámetro |
| TIPODATO | VARCHAR2(10) | | Tipo (String, Number, Boolean) |
| ESTADO | CHAR(1) | | 'T' = Activo, 'F' = Inactivo |
| DESCRIPCION | VARCHAR2(255) | | Documentación del parámetro |

**Uso en ACE:** En las interfaces, se crea la variable `Environment.Parámetros.[Parametro]` con el Valor correspondiente.

---

## Tabla: CORREOSDESTINATARIOS

**Propósito:** Configuración de destinatarios de correos para cada aplicación.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDAPP | NUMBER | PK, FK → APLICACIONES | Referencia a la aplicación |
| TIPOCORREO | VARCHAR2(15) | PK | Tipo de correo (ej: Error, Info) |
| IDENTIFICADOR | VARCHAR2(15) | PK | Identificador del destinatario |
| CAMPO | VARCHAR2(3) | PK | Parte del correo (To, Cc, Bcc) |
| ORDEN | NUMBER | PK | Orden para múltiples destinatarios |
| VALOR | VARCHAR2(50) | | Dirección de correo |
| ESTADO | CHAR(1) | | 'T' = Activo, 'F' = Inactivo |

---

## Tabla: EVENTOS (la más importante)

**Propósito:** Log principal. Registra cada evento de las interfaces (envíos, recepciones, errores, etc.)

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDEVENTO | NUMBER | PK | Secuencia única (seq_eventos) |
| IDAPP | NUMBER | FK → APLICACIONES | Qué app generó el evento |
| VERSION | VARCHAR2(20) | | Versión de la app al momento del evento |
| FECHAHORA | TIMESTAMP | | Cuándo ocurrió (default SYSTIMESTAMP) |
| DATO1 | VARCHAR2(100) | | Dato auxiliar (significado según APLICACIONES.DESCDATO1) |
| DATO2 | VARCHAR2(100) | | Dato auxiliar (significado según APLICACIONES.DESCDATO2) |
| DATO3 | VARCHAR2(100) | | Dato auxiliar (significado según APLICACIONES.DESCDATO3) |

**Importante:** Los campos DATO1, DATO2, DATO3 son "atajos" para filtrado rápido. El significado exacto de cada uno varía según la aplicación y está documentado en APLICACIONES.DESCDATON.

---

## Tabla: EVENTOSDETALLES

**Propósito:** Almacena los detalles variables de cada evento. Un evento puede tener múltiples detalles.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDEVENTO | NUMBER | PK, FK → EVENTOS | Referencia al evento padre |
| DESCDATO | VARCHAR2(50) | PK | Nombre del detalle (ej: "Resultado", "MensajeError") |
| DATO | VARCHAR2(300) | | Valor del detalle (ej: "OK", "Timeout conectando al SAP") |

**Ejemplo de uso:**
- Un evento con IDEVENTO=123 puede tener:
  - DESCDATO="Resultado", DATO="OK"
  - DESCDATO="TiempoMs", DATO="245"
  - DESCDATO="PayloadSize", DATO="4096"

---

## Tabla: ARCHIVOSPROCESADOS

**Propósito:** Registro de archivos recibidos y procesados por las interfaces.

| Campo | Tipo | ¿PK/FK? | Descripción |
| :--- | :--- | :--- | :--- |
| IDEVENTO | NUMBER | PK, FK → EVENTOS | Referencia al evento relacionado |
| ARCHIVO | VARCHAR2(80) | NOT NULL | Nombre del archivo procesado |
| ESTADO | VARCHAR2(25) | | Estado (Recibido, OK, Error, etc.) |
| FECHAHORA | TIMESTAMP | | Cuándo se procesó (default SYSTIMESTAMP) |

**Índices:**
- `idx_archivosprocesados_archivo`: para búsquedas por nombre de archivo
- `idx_archivo_estado`: para filtros combinados

---

## Relaciones Clave (Diagrama Conceptual)
APLICACIONES (1) ──────< (N) VERSIONES
│
└───────────────< (N) PARAMETROS
│
└───────────────< (N) CORREOSDESTINATARIOS
│
└───────────────< (N) EVENTOS ──────< (N) EVENTOSDETALLES
│
└──────< (1) ARCHIVOSPROCESADOS

## Consultas SQL Típicas para el Dashboard

### 1. Últimos eventos con detalles de la aplicación

SELECT e.IDEVENTO, a.APP, e.VERSION, e.FECHAHORA, 
       e.DATO1, e.DATO2, e.DATO3
FROM EVENTOS e
JOIN APLICACIONES a ON e.IDAPP = a.IDAPP
ORDER BY e.FECHAHORA DESC
FETCH FIRST 50 ROWS ONLY

### 2. EVENTOS con sus detalles completos

SELECT e.IDEVENTO, a.APP, e.FECHAHORA,
       ed.DESCDATO, ed.DATO
FROM EVENTOS e
JOIN APLICACIONES a ON e.IDAPP = a.IDAPP
JOIN EVENTOSDETALLES ed ON e.IDEVENTO = ed.IDEVENTO
WHERE e.FECHAHORA >= SYSDATE - 7
ORDER BY e.FECHAHORA DESC

### 3. Buscar errores por aplicación

SELECT e.IDEVENTO, a.APP, e.FECHAHORA, ed.DATO
FROM EVENTOS e
JOIN APLICACIONES a ON e.IDAPP = a.IDAPP
JOIN EVENTOSDETALLES ed ON e.IDEVENTO = ed.IDEVENTO
WHERE ed.DESCDATO = 'Resultado' 
  AND ed.DATO != 'OK'
ORDER BY e.FECHAHORA DESC

### 4. Obtener el significado de DATO1 para una app

SELECT APP, DESCDATO1, DESCDATO2, DESCDATO3
FROM APLICACIONES
WHERE APP = :app_seleccionada


## Notas para el Dashboard en Reflex

- Los campos DATO1-3 son de búsqueda rápida, pero los detalles reales están en EVENTOSDETALLES

- Relación crítica: EVENTOS → EVENTOSDETALLES es 1 a N

- Los nombres de las apps vienen de APLICACIONES.APP

- Para reportes, usar APLICACIONES.DESCDATON como títulos de columna

