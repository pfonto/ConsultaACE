"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import oracledb

from rxconfig import config


class State(rx.State):
    # Lista para almacenar las opciones del selector
    opciones_app: list[str] = []
    app_seleccionada: str = ""

    @rx.event
    def obtener_aplicaciones(self):
        """Obtiene los nombres de las aplicaciones desde Oracle."""
        try:
            # Configuración de conexión
            conn = oracledb.connect(
                user="IIBUSR",
                password="Iibusr#826",
                dsn="(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=VDW-FidelidadAIX.gdisco)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=IIB)))"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT App FROM Aplicaciones ORDER BY App")
            # Extraemos el primer elemento de cada tupla devuelta
            self.opciones_app = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error de conexión: {e}")
            self.opciones_app = ["Error al cargar"]

    @rx.event
    def asignar_seleccion(self, valor: str):
        # Aquí se podrían agregar validaciones o lógica extra
        self.app_seleccionada = valor

    @rx.event
    def consultar(self) -> None:
        """Manejador para la consulta."""
        print(f"Consultando interfaz: {self.app_seleccionada}")

def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.hstack(
            rx.input(placeholder="Interface", name="interface", required=True),
            rx.select(
                State.opciones_app,
                placeholder="Seleccione Interface",
                on_change=State.asignar_seleccion,
                required=True,
            ),
            rx.input(placeholder="Fecha Desde", name="fecha_desde"),
            rx.input(placeholder="Fecha Hasta", name="fecha_hasta"),
            rx.button("Consultar", on_click=State.consultar)
        )
    )


app = rx.App()
# app.add_page(index)
app.add_page(index, on_load=State.obtener_aplicaciones)