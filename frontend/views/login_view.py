import math
import re
import flet as ft


def main(page: ft.Page):
    # Configuración básica
    page.title = "Pharmastock - Login"
    page.bgcolor = "#EAF2FF"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Paleta de colores
    COLOR_AZUL_CARD = "#3B71E8"
    COLOR_INPUT_BG = "#2B53B4"
    COLOR_TEXTO_MUTED = "#D0E0FF"
    COLOR_TEXTO_LABEL = "#79A8E4"
    COLOR_BORDER = "#84ACFF"
    COLOR_ERROR = "#D43838"

    # Paleta de colores - Modal
    COLOR_TITULO_MODAL = "#0B2B63"
    COLOR_SUBTITULO_MODAL = "#5A73A3"
    COLOR_INPUT_BG_MODAL = "#EBF3FE"
    COLOR_INPUT_BORDER_MODAL = "#99C1F1"
    COLOR_BOTON_MODAL = "#7F96C5"

   
    # --- CAMPOS Y VISTA DEL LOGIN ---
    input_usuario = ft.TextField(
        hint_text="ejemplo@gmail.com",
        hint_style=ft.TextStyle(color=COLOR_TEXTO_LABEL),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_radius=30,
        content_padding=ft.Padding.symmetric(horizontal=15, vertical=10),
        height=45,
        width=float("inf"),
    )

    error_usuario = ft.Text("", color=COLOR_ERROR, size=12, visible=False)

    input_password = ft.TextField(
        hint_text="Ingresa tu contraseña",
        hint_style=ft.TextStyle(color=COLOR_TEXTO_LABEL),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_radius=30,
        password=True,
        suffix=ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.VISIBILITY_OFF,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: toggle_password(e),
            ),
            margin=ft.Margin.only(right=-8),
        ),
        content_padding=ft.Padding.symmetric(horizontal=15, vertical=10),
        height=45,
        width=float("inf"),
    )

    error_password = ft.Text("", color=COLOR_ERROR, size=12, visible=False)

    def toggle_password(e):
        input_password.password = not input_password.password
        e.control.icon = (
            ft.Icons.VISIBILITY
            if not input_password.password
            else ft.Icons.VISIBILITY_OFF
        )
        input_password.update()

    def validar_login(e):
        val_user = input_usuario.value.strip() if input_usuario.value else ""
        val_pass = input_password.value.strip() if input_password.value else ""

        es_valido = True

        if not val_user:
            error_usuario.value = "El usuario o correo es obligatorio"
            error_usuario.visible = True
            input_usuario.border_color = COLOR_ERROR
            es_valido = False
        else:
            error_usuario.visible = False
            input_usuario.border_color = COLOR_BORDER

        if not val_pass:
            error_password.value = "La contraseña es obligatoria"
            error_password.visible = True
            input_password.border_color = COLOR_ERROR
            es_valido = False
        else:
            error_password.visible = False
            input_password.border_color = COLOR_BORDER

        error_usuario.update()
        input_usuario.update()
        error_password.update()
        input_password.update()

        if es_valido:
            print("Iniciando sesión...")

    # --- TARJETAS DEL LOGIN ---
    tarjeta_izquierda = ft.Container(
        width=400,
        height=450,
        bgcolor="#99FFFFFF",
        border_radius=ft.BorderRadius.all(16),
        padding=ft.Padding.all(30),
        blur=ft.Blur(3, 3),
        border=ft.Border.all(1, "#FFFFFF"),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(-5, 5),
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Image(
                    src="Logo_PharmaStockCompleto_SinFondo.png",
                    width=400,
                    height=350,
                    fit="contain",
                ),
            ],
        ),
    )

    tarjeta_derecha = ft.Container(
        width=650,
        height=620,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment(0.8, 1),
            tile_mode=ft.GradientTileMode.MIRROR,
            rotation=math.pi / 4,
            colors=["#99B7F3", "#5A8FEE", "#2168E5", "#0A3277"],
        ),
        border_radius=ft.BorderRadius.all(16),
        padding=ft.Padding.all(30),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.BLACK26,
            offset=ft.Offset(5, 5),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text(
                    "Iniciar sesión",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    margin=ft.Margin.only(top=-8),
                    content=ft.Text(
                        "Ingrese sus datos:",
                        size=18,
                        color=COLOR_TEXTO_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
                ft.Container(height=30),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=3,
                    width=float("inf"),
                    controls=[
                        ft.Text(
                            "Correo electrónico / Número telefónico",
                            size=18,
                            color=COLOR_TEXTO_MUTED,
                            weight=ft.FontWeight.W_400,
                        ),
                        input_usuario,
                        error_usuario,
                    ],
                ),
                ft.Container(height=5),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=3,
                    width=float("inf"),
                    controls=[
                        ft.Text(
                            "Contraseña",
                            size=18,
                            color=COLOR_TEXTO_MUTED,
                            weight=ft.FontWeight.W_400,
                        ),
                        input_password,
                        error_password,
                    ],
                ),
                ft.Container(
                    margin=ft.Margin.symmetric(vertical=6),
                    content=ft.Text(
                        "- - " * 25,
                        color=COLOR_BORDER,
                        size=20,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                    ),
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Iniciar sesión",
                        color=COLOR_AZUL_CARD,
                        weight=ft.FontWeight.BOLD,
                        size=18,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=30),
                    ),
                    width=float("inf"),
                    height=42,
                    on_click=validar_login,
                ),
                ft.TextButton(
                    content=ft.Text(
                        "Olvidé mi contraseña",
                        color=ft.Colors.WHITE,
                        size=16,
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.UNDERLINE,
                            decoration_color=ft.Colors.WHITE,
                        ),
                    ),
                    on_click=abrir_recuperacion,
                ),
            ],
        ),
    )

    tarjetas_unidas = ft.Row(
        controls=[tarjeta_izquierda, tarjeta_derecha],
        spacing=-15,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # MONTAJE DE LA PANTALLA: Fondo + Login + Modal
    pantalla_completa = ft.Stack(
        controls=[
            ft.Image(
                src="fondo.png",
                width=float("inf"),
                height=float("inf"),
                fit="cover",
            ),
            ft.Container(
                content=tarjetas_unidas,
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
            capa_modal,  # El modal queda encima de todo pero con visible=False por defecto
        ],
        expand=True,
    )

    page.add(pantalla_completa)


ft.app(target=main, assets_dir="assets")