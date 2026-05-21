import reflex as rx
from ConsultaACE.db import SessionLocal
from ConsultaACE.models import Aplicacion, Evento, EventoDetalle
from sqlalchemy import select
from datetime import date, datetime, timedelta
from typing import Any


class State(rx.State):
    opciones_app: list[str] = []
    app_seleccionada: str = ""
    opciones_dato1: list[str] = []
    opciones_dato2: list[str] = []
    opciones_dato3: list[str] = []
    dato1_seleccionado: str = ""
    dato2_seleccionado: str = ""
    dato3_seleccionado: str = ""
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
    columnas_dinamicas: list[str] = []

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
        self.opciones_dato1 = []
        self.opciones_dato2 = []
        self.opciones_dato3 = []
        self.dato1_seleccionado = ""
        self.dato2_seleccionado = ""
        self.dato3_seleccionado = ""
        self.columnas_dinamicas = []

        if not valor:
            return

        db = SessionLocal()
        try:
            app_row = db.execute(
                select(Aplicacion.IdApp, Aplicacion.DescDato1, Aplicacion.DescDato2, Aplicacion.DescDato3)
                .where(Aplicacion.App == valor)
            ).first()

            if app_row:
                self.app_desc_dato1 = app_row.DescDato1 or ""
                self.app_desc_dato2 = app_row.DescDato2 or ""
                self.app_desc_dato3 = app_row.DescDato3 or ""

                d1 = db.execute(
                    select(Evento.Dato1).distinct()
                    .where(Evento.IdApp == app_row.IdApp)
                    .where(Evento.Dato1.isnot(None))
                    .order_by(Evento.Dato1)
                ).scalars().all()
                self.opciones_dato1 = list(d1)

                d2 = db.execute(
                    select(Evento.Dato2).distinct()
                    .where(Evento.IdApp == app_row.IdApp)
                    .where(Evento.Dato2.isnot(None))
                    .order_by(Evento.Dato2)
                ).scalars().all()
                self.opciones_dato2 = list(d2)

                d3 = db.execute(
                    select(Evento.Dato3).distinct()
                    .where(Evento.IdApp == app_row.IdApp)
                    .where(Evento.Dato3.isnot(None))
                    .order_by(Evento.Dato3)
                ).scalars().all()
                self.opciones_dato3 = list(d3)

                if valor == "Financieras":
                    self.columnas_dinamicas = ["CantidadRegistros", "Importe", "MontoACobrar"]

        except Exception as e:
            print(f"Error al cargar datos de la interface: {e}")
        finally:
            db.close()

    @rx.event
    def asignar_dato1(self, valor: str):
        self.dato1_seleccionado = valor

    @rx.event
    def asignar_dato2(self, valor: str):
        self.dato2_seleccionado = valor

    @rx.event
    def asignar_dato3(self, valor: str):
        self.dato3_seleccionado = valor

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
        self.cargar_eventos(
            self.app_seleccionada, self.fecha_desde, self.fecha_hasta,
            self.dato1_seleccionado, self.dato2_seleccionado, self.dato3_seleccionado,
        )

    def cargar_eventos(self, app: str, desde: str, hasta: str, dato1: str = "", dato2: str = "", dato3: str = ""):
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
            if dato1:
                stmt = stmt.where(Evento.Dato1 == dato1)
            if dato2:
                stmt = stmt.where(Evento.Dato2 == dato2)
            if dato3:
                stmt = stmt.where(Evento.Dato3 == dato3)

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

            ids = [r[0] for r in rows]
            detail_keys = ["Resultado"]
            for col_name in self.columnas_dinamicas:
                detail_keys.append(col_name)

            if ids:
                detail_rows = db.execute(
                    select(EventoDetalle.IdEvento, EventoDetalle.DescDato, EventoDetalle.Dato)
                    .where(EventoDetalle.IdEvento.in_(ids))
                    .where(EventoDetalle.DescDato.in_(detail_keys))
                ).all()

                det_map: dict[int, dict[str, str]] = {}
                for dr in detail_rows:
                    det_map.setdefault(dr[0], {})[dr[1]] = dr[2] or ""

                for ev in self.eventos:
                    det = det_map.get(ev["id_evento"], {})
                    ev["resultado"] = det.get("Resultado", "")
                    if "CantidadRegistros" in self.columnas_dinamicas:
                        ev["cantidad_registros"] = det.get("CantidadRegistros", "")
                    if "Importe" in self.columnas_dinamicas:
                        ev["importe"] = det.get("Importe", "")
                    if "MontoACobrar" in self.columnas_dinamicas:
                        ev["monto_a_cobrar"] = det.get("MontoACobrar", "")

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
        rx.table.cell(evento.get("resultado", "")),
        rx.cond(
            State.columnas_dinamicas.contains("CantidadRegistros"),
            rx.table.cell(evento.get("cantidad_registros", "")),
        ),
        rx.cond(
            State.columnas_dinamicas.contains("Importe"),
            rx.table.cell(evento.get("importe", "")),
        ),
        rx.cond(
            State.columnas_dinamicas.contains("MontoACobrar"),
            rx.table.cell(evento.get("monto_a_cobrar", "")),
        ),
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
                        rx.table.column_header_cell("Resultado"),
                        rx.cond(
                            State.columnas_dinamicas.contains("CantidadRegistros"),
                            rx.table.column_header_cell("CantidadRegistros"),
                        ),
                        rx.cond(
                            State.columnas_dinamicas.contains("Importe"),
                            rx.table.column_header_cell("Importe"),
                        ),
                        rx.cond(
                            State.columnas_dinamicas.contains("MontoACobrar"),
                            rx.table.column_header_cell("MontoACobrar"),
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
                style={"min_width": "max-content"},
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
        rx.vstack(
            rx.heading(
                "Consulta de Interfaces de ACE",
                size="7",
                text_align="center",
                width="100%",
            ),
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
                justify="center",
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.select(
                    State.opciones_dato1,
                    placeholder=State.app_desc_dato1,
                    value=State.dato1_seleccionado,
                    disabled=State.app_seleccionada == "",
                    on_change=State.asignar_dato1,
                ),
                rx.select(
                    State.opciones_dato2,
                    placeholder=State.app_desc_dato2,
                    value=State.dato2_seleccionado,
                    disabled=State.app_seleccionada == "",
                    on_change=State.asignar_dato2,
                ),
                rx.select(
                    State.opciones_dato3,
                    placeholder=State.app_desc_dato3,
                    value=State.dato3_seleccionado,
                    disabled=State.app_seleccionada == "",
                    on_change=State.asignar_dato3,
                ),
                justify="center",
                spacing="3",
                width="100%",
            ),
            rx.button(
                "Consultar",
                on_click=State.consultar,
                disabled=(State.error_fecha != "") | (State.fecha_desde == "") | (State.fecha_hasta == "") | (State.app_seleccionada == ""),
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
            spacing="3",
            width="100%",
            align="center",
        ),
    )


app = rx.App()
app.add_page(index, on_load=State.obtener_aplicaciones)
