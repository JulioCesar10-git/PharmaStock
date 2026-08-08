import flet as ft

from components.calendario import crear_tarjeta_calendario
from components.ganancias import crear_tarjeta_ganancias
from components.avisos import crear_tarjeta_avisos


def vista_general(page: ft.Page, fecha_activa: dict, modulo_recordatorios: dict, cambiar_pestana_callback=None):
    return ft.Row(
        [
            # Columna izquierda: calendario + ganancias
            ft.Column(
                [
                    crear_tarjeta_calendario(page, fecha_activa, modulo_recordatorios["abrir_modal_recordatorio"]),
                    crear_tarjeta_ganancias(),
                ],
                expand=1,
                scroll=ft.ScrollMode.AUTO,
            ),

            # Columna central: tareas
            ft.Column(
                [
                    modulo_recordatorios["crear_tarjeta_tareas"](),
                ],
                expand=1,
            ),

            # Columna derecha: avisos
            ft.Column(
                [
                    crear_tarjeta_avisos(cambiar_pestana_callback),
                ],
                expand=1,
            ),
        ],
        spacing=15,
        expand=True,
    )