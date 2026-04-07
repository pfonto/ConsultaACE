"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config


class State(rx.State):
    """The app state."""

    @rx.event
    def consultar(self) -> None:
        """Manejador para la consulta."""
        print("Consultar")


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        rx.hstack(
            rx.input(placeholder="Interface", name="interface", required=True),
            rx.input(placeholder="Fecha Desde", name="fecha_desde"),
            rx.input(placeholder="Fecha Hasta", name="fecha_hasta"),
            rx.button("Consultar", on_click=State.consultar)
        )
    )


app = rx.App()
app.add_page(index)
