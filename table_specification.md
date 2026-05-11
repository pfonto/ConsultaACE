# Especificación: Tabla de Eventos con rx.table.root

## Objetivo
Crear un componente de tabla en Reflex que muestre los eventos de la base de datos Oracle **filtrados por los criterios seleccionados por el usuario**, usando rx.table.root para un renderizado eficiente.

## Flujo de datos completo

Usuario selecciona Interface
↓
Usuario ingresa Fecha Desde
↓
Usuario ingresa Fecha Hasta
↓
Usuario presiona botón "Consultar"
↓
Se ejecuta consulta SQL con los 3 filtros
↓
Se actualiza el State con los resultados
↓
La tabla se re-renderiza automáticamente

## Estructura del componente

### Esqueleto base

rx.vstack(
            rx.table.root(
                rx.table.header(...),
                rx.table.body(...),
                width="100%",
            ),
            width="100%",
            margin_top="20px",
        )
		

### Columnas necesarias
	Columna		Título			Proviene de								Descripción
	FechaHora	"Fecha y Hora"	Eventos.FechaHora						Formatear como dd/mm/yyyy HH:MM:SS
	App			"Aplicación"	Aplicaciones.App						Nombre de la interfaz
	Version		"Versión"		Eventos.Version							Versión cuando ocurrió
	Dato1		(dinámico)		Eventos.Dato1 + Aplicaciones.DescDato1	Usar el título de la tabla Aplicaciones
	Dato2		(dinámico)		Eventos.Dato2 + Aplicaciones.DescDato2	Usar el título de la tabla Aplicaciones
	Dato3		(dinámico)		Eventos.Dato3 + Aplicaciones.DescDato3	Usar el título de la tabla Aplicaciones
	Detalles	"Detalles"		EventosDetalles							Mostrar como tooltip o modal
	
###Comportamiento esperado
	- Filas ordenables por fecha (más reciente primero)
	- Scroll horizontal si hay muchas columnas
	- Tooltip en "Detalles" que muestre todos los DescDato/Dato
	- Opcional: paginación (mostrar 20 eventos por defecto)

## SQL de carga de datos

### Query principal

SELECT 
    e.IdEvento,
    e.FechaHora,
    a.App,
    e.Version,
    e.Dato1,
    e.Dato2,
    e.Dato3,
    a.DescDato1,
    a.DescDato2,
    a.DescDato3
FROM Eventos e
JOIN Aplicaciones a ON e.IdApp = a.IdApp
ORDER BY e.FechaHora DESC
FETCH FIRST 50 ROWS ONLY

### Query para detalles (cuando el usuario hace click)

SELECT DescDato, Dato
FROM EventosDetalles
WHERE IdEvento = :id_evento
ORDER BY DescDato

##Integración con el State existente

### Actualmente en ConsultaACE.py tengo:

class State(rx.State):
    opciones_app: list[str] = []
    app_seleccionada: str = ""
    
    @rx.event
    def obtener_aplicaciones(self):
        # ... existe
        
    @rx.event
    def consultar(self) -> None:
        # ... pendiente
		
Necesito:
1. Un nuevo estado eventos: list[dict] = [] para almacenar los resultados
2. Un método cargar_eventos(app: str, desde: str, hasta: str) que ejecute la query
3. Un método obtener_detalles(id_evento: int) para el tooltip
4. Modificar consultar() para que llame a cargar_eventos() con los valores del formulario

## Requisitos de estilo

- Ancho de tabla: 100%
- Bordes sutiles
- Filas con hover
- Cabecera fija al hacer scroll

## Opcional (futuro)

- Paginación con rx.cond
- Filtros por columna
- Exportar a CSV
