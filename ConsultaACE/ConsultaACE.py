import reflex as rx
from ConsultaACE.db import SessionLocal
from ConsultaACE.models import Aplicacion, Evento, EventoDetalle
from sqlalchemy import select
from datetime import date, datetime, timedelta
from typing import Any


class State(rx.State):
    opciones_app: list[str] = []
    app_seleccionada: str = ""
    fecha_desde: str = ""
    fecha_hasta: str = ""
    error_fecha: str = ""
    hoy: str = date.today().isoformat()

    eventos: list[dict[str, Any]] = []
    app_desc_dato1: str = ""
    app_desc_dato2: str = ""
    app_desc_dato3: str = ""
    detalles_actuales: list[dict[str, str]] = []
    mostrar_detalles_modal: bool = False
    evento_seleccionado_id: int = 0
    total_eventos: int = 0

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
        self.app_seleccionada = valor
        self.app_desc_dato1 = ""
        self.app_desc_dato2 = ""
        self.app_desc_dato3 = ""

    @rx.event
    def actualizar_fecha(self, nombre: str, valor: str):
        if nombre == "fecha_desde":
            self.fecha_desde = valor
        elif nombre == "fecha_hasta":
            self.fecha_hasta = valor
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
        self.cargar_eventos(self.app_seleccionada, self.fecha_desde, self.fecha_hasta)

    def cargar_eventos(self, app: str, desde: str, hasta: str):
        db = SessionLocal()
        try:
            stmt = (
                select(
                    Evento.IdEvento,
                    Evento.FechaHora,
                    Aplicacion.App,
                    Evento.Version,
                    Evento.Dato1,
                    Evento.Dato2,
                    Evento.Dato3,
                    Aplicacion.DescDato1,
                    Aplicacion.DescDato2,
                    Aplicacion.DescDato3,
                )
                .join(Aplicacion, Evento.IdApp == Aplicacion.IdApp)
                .order_by(Evento.FechaHora.desc())
                .limit(50)
            )

            if app:
                stmt = stmt.where(Aplicacion.App == app)
            if desde:
                desde_dt = datetime.fromisoformat(desde)
                stmt = stmt.where(Evento.FechaHora >= desde_dt)
            if hasta:
                hasta_dt = datetime.fromisoformat(hasta) + timedelta(days=1)
                stmt = stmt.where(Evento.FechaHora < hasta_dt)

            rows = db.execute(stmt).all()
            self.eventos = [
                {
                    "id_evento": r[0],
                    "fecha_hora": r[1].strftime('%d/%m/%Y %H:%M:%S') if r[1] else "",
                    "app": r[2],
                    "version": r[3],
                    "dato1": r[4] or "",
                    "dato2": r[5] or "",
                    "dato3": r[6] or "",
                    "desc_dato1": r[7] or "",
                    "desc_dato2": r[8] or "",
                    "desc_dato3": r[9] or "",
                }
                for r in rows
            ]

            self.total_eventos = len(rows)
            if self.eventos:
                self.app_desc_dato1 = self.eventos[0]["desc_dato1"]
                self.app_desc_dato2 = self.eventos[0]["desc_dato2"]
                self.app_desc_dato3 = self.eventos[0]["desc_dato3"]
            else:
                self.app_desc_dato1 = ""
                self.app_desc_dato2 = ""
                self.app_desc_dato3 = ""

        except Exception as e:
            print(f"Error al consultar eventos: {e}")
            self.eventos = []
            self.total_eventos = 0
        finally:
            db.close()

    @rx.event
    def cargar_detalles(self, id_evento: int):
        self.evento_seleccionado_id = id_evento
        db = SessionLocal()
        try:
            stmt = (
                select(EventoDetalle.DescDato, EventoDetalle.Dato)
                .where(EventoDetalle.IdEvento == id_evento)
                .order_by(EventoDetalle.DescDato)
            )
            rows = db.execute(stmt).all()
            self.detalles_actuales = [
                {"desc_dato": r[0], "dato": r[1]} for r in rows
            ]
            self.mostrar_detalles_modal = True
        except Exception as e:
            print(f"Error al cargar detalles: {e}")
            self.detalles_actuales = []
        finally:
            db.close()

    @rx.event
    def cerrar_modal(self):
        self.mostrar_detalles_modal = False
        self.detalles_actuales = []


def render_fila(evento: dict[str, Any]) -> rx.Component:
    return rx.table.row(
        rx.table.cell(evento["fecha_hora"]),
        rx.table.cell(evento["app"]),
        rx.table.cell(evento["version"]),
        rx.table.cell(evento["dato1"]),
        rx.table.cell(evento["dato2"]),
        rx.table.cell(evento["dato3"]),
        rx.table.cell(
            rx.button(
                "Detalles",
                size="1",
                on_click=State.cargar_detalles(evento["id_evento"]),
            )
        ),
        _hover={"background_color": "var(--gray-a3)"},
    )


def tabla_eventos() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Fecha y Hora"),
                        rx.table.column_header_cell("Aplicación"),
                        rx.table.column_header_cell("Versión"),
                        rx.table.column_header_cell(
                            rx.cond(State.app_desc_dato1 != "", State.app_desc_dato1, "Dato1")
                        ),
                        rx.table.column_header_cell(
                            rx.cond(State.app_desc_dato2 != "", State.app_desc_dato2, "Dato2")
                        ),
                        rx.table.column_header_cell(
                            rx.cond(State.app_desc_dato3 != "", State.app_desc_dato3, "Dato3")
                        ),
                        rx.table.column_header_cell("Detalles"),
                    ),
                    style={"position": "sticky", "top": 0, "z_index": 10, "background_color": "var(--gray-1)"},
                ),
                rx.table.body(
                    rx.foreach(State.eventos, render_fila),
                ),
                variant="surface",
                size="2",
                width="100%",
            ),
            width="100%",
            overflow_x="auto",
            overflow_y="auto",
            max_height="600px",
        ),
        rx.cond(
            State.eventos,
            rx.text(
                f"Mostrando {State.total_eventos} eventos",
                font_size="0.85em",
                color_scheme="gray",
            ),
            rx.fragment(),
        ),
        width="100%",
        margin_top="20px",
    )


def dialog_detalles() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(f"Detalles del evento #{State.evento_seleccionado_id}"),
            rx.vstack(
                rx.foreach(
                    State.detalles_actuales,
                    lambda d: rx.hstack(
                        rx.text(d["desc_dato"], font_weight="bold", min_width="120px"),
                        rx.text(d["dato"]),
                        width="100%",
                    ),
                ),
                spacing="2",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cerrar", on_click=State.cerrar_modal),
                ),
                justify="end",
                margin_top="16px",
            ),
        ),
        open=State.mostrar_detalles_modal,
    )


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
                disabled=(State.error_fecha != "") | (State.fecha_desde == "") | (State.fecha_hasta == ""),
            ),
        ),
        rx.cond(
            State.error_fecha != "",
            rx.text(State.error_fecha, color="red", font_size="0.9em"),
            None,
        ),
        rx.cond(
            State.eventos,
            tabla_eventos(),
            None,
        ),
        dialog_detalles(),
    )


app = rx.App()
app.add_page(index, on_load=State.obtener_aplicaciones)
