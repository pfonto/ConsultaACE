import reflex as rx
from ConsultaACE.db import SessionLocal
from ConsultaACE.models import Aplicacion
from sqlalchemy import select

class State(rx.State):
    opciones_app: list[str] = []
    app_seleccionada: str = ""

    @rx.event
    def obtener_aplicaciones(self):
        db = SessionLocal()
        try:
            apps = db.execute(select(Aplicacion.App).order_by(Aplicacion.App)).scalars().all()
            self.opciones_app = list(apps)
        except Exception as e:
            print(f"Error: {e}")
            self.opciones_app = ["Error al cargar"]
        #except Exception as e:
        #    print(f"Error inesperado: {e}")
        #    self.opciones_app = ["Error al cargar"]
        finally:
            db.close()

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
            # rx.input(placeholder="Interface", name="interface", required=True),
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