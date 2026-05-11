import reflex as rx
from ConsultaACE.db import SessionLocal
from ConsultaACE.models import Aplicacion
from sqlalchemy import select


from datetime import date

class State(rx.State):
    opciones_app: list[str] = []
    app_seleccionada: str = ""
    fecha_desde: str = ""
    fecha_hasta: str = ""
    error_fecha: str = ""
    hoy: str = date.today().isoformat()

    @rx.event
    def obtener_aplicaciones(self):
        db = SessionLocal()
        try:
            apps = db.execute(select(Aplicacion.App).order_by(Aplicacion.App)).scalars().all()
            self.opciones_app = list(apps)
        except Exception as e:
            print(f"Error: {e}")
            self.opciones_app = ["Error al cargar"]
        finally:
            db.close()

    @rx.event
    def asignar_seleccion(self, valor: str):
        # Aquí se podrían agregar validaciones o lógica extra
        self.app_seleccionada = valor

    @rx.event
    def actualizar_fecha(self, nombre: str, valor: str):
        if nombre == "fecha_desde":
            self.fecha_desde = valor
        elif nombre == "fecha_hasta":
            self.fecha_hasta = valor
        # Validación en tiempo real
        self.error_fecha = ""
        if self.fecha_desde:
            if self.fecha_desde > self.hoy:
                self.error_fecha = "La fecha 'Desde' debe ser menor o igual a la fecha actual."
        if self.fecha_desde and self.fecha_hasta:
            if self.fecha_hasta < self.fecha_desde:
                self.error_fecha = "La fecha 'Hasta' debe ser mayor o igual a la fecha 'Desde' y menor o igual a la fecha actual."
            elif self.fecha_hasta > self.hoy:
                self.error_fecha = "La fecha 'Hasta' debe ser menor o igual a la fecha actual."

    @rx.event
    def consultar(self) -> None:
        """Manejador para la consulta."""
        print(f"Consultando interfaz: {self.app_seleccionada}")


def index() -> rx.Component:
    return rx.container(
        rx.hstack(
            rx.select(
                State.opciones_app,
                placeholder="Seleccione Interface",
                on_change=State.asignar_seleccion,
                required=True,
            ),
            rx.input(
                type="date",
                name="fecha_desde",
                value=State.fecha_desde,
                max=State.hoy,
                on_change=lambda e: State.actualizar_fecha("fecha_desde", e),
                required=True,
            ),
            rx.input(
                type="date",
                name="fecha_hasta",
                value=State.fecha_hasta,
                min=State.fecha_desde,
                max=State.hoy,
                on_change=lambda e: State.actualizar_fecha("fecha_hasta", e),
                required=True,
            ),
            rx.button(
                "Consultar",
                on_click=State.consultar,
                #disabled=State.error_fecha != "" or State.fecha_desde == "" or State.fecha_hasta == ""
                disabled=(State.error_fecha != "") | (State.fecha_desde == "") | (State.fecha_hasta == "")
            )
        ),
        rx.cond(
            State.error_fecha != "",
            rx.text(State.error_fecha, color="red", font_size="0.9em"),
            None
        )
    )


app = rx.App()
# app.add_page(index)
app.add_page(index, on_load=State.obtener_aplicaciones)