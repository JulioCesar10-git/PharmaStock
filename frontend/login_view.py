import math
import socket
import flet as ft

from frontend.theme import colores

# IMPORTAR BACKEND
from backend.dao.usuario_dao import UsuarioDAO

def vista_login(page: ft.Page, on_login_exitoso=None):
    """
    Construye y devuelve el contenido de la pantalla de login.
    on_login_exitoso: función opcional que se llama cuando el login es válido
                       (por ejemplo, para cambiar a la ventana principal).
    """
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

    # Paleta de colores - Modal (mismos colores/tamaños que "Añadir empleado")
    c = colores()
    COLOR_TITULO_MODAL = c["input_bg"]
    COLOR_SUBTITULO_MODAL = c["input_bg"]
    COLOR_LABEL_MODAL = "#004C95"
    COLOR_INPUT_BG_MODAL = "#E9F5FF"
    COLOR_INPUT_BORDER_MODAL = c["borde_campo"]
    COLOR_BOTON_MODAL = c["boton_secundario"]

    # --- COMPONENTES DE LA VENTANA EMERGENTE ---
    input_correo_recuperar = ft.TextField(
        hint_text="ejemplo@gmail.com",
        hint_style=ft.TextStyle(color=ft.Colors.with_opacity(0.45, COLOR_INPUT_BORDER_MODAL), size=18),
        text_style=ft.TextStyle(color=COLOR_INPUT_BORDER_MODAL, size=18),
        bgcolor=COLOR_INPUT_BG_MODAL,
        border_color=COLOR_INPUT_BORDER_MODAL,
        border_radius=30,
        content_padding=ft.Padding.only(left=15),
        height=45,
        width=float("inf"),
    )

    error_recuperar = ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    capa_modal = ft.Container(
        visible=False,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.BLACK54,  
        expand=True,
    )

    # Funciones de ventana emergente
    def abrir_recuperacion(e):
        capa_modal.visible = True
        page.update()

    def cerrar_modal(e):
        capa_modal.visible = False
        input_correo_recuperar.value = ""
        input_correo_recuperar.border_color = COLOR_INPUT_BORDER_MODAL
        error_recuperar.visible = False
        page.update()

    def hay_conexion_internet(timeout=3):
        """Intenta abrir un socket a un servidor DNS público para confirmar
        si hay conexión a internet. No depende de que un sitio web específico
        esté disponible, solo de que haya salida a la red."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            return False

    def enviar_correo_recuperacion(e):
        correo = input_correo_recuperar.value or ""

        if not correo:
            error_recuperar.value = "Por favor ingresa tu correo"
            error_recuperar.visible = True
            input_correo_recuperar.border_color = COLOR_ERROR
            page.update()
        elif " " in correo:
            error_recuperar.value = "No puedes dejar espacios al ingresar un correo"
            error_recuperar.visible = True
            input_correo_recuperar.border_color = COLOR_ERROR
            page.update()
        elif "@" not in correo:
            error_recuperar.value = "Es necesario colocar un @ en el correo"
            error_recuperar.visible = True
            input_correo_recuperar.border_color = COLOR_ERROR
            page.update()
        elif not hay_conexion_internet():
            error_recuperar.value = ""
            error_recuperar.visible = False
            input_correo_recuperar.border_color = COLOR_INPUT_BORDER_MODAL
            page.update()

            # Notificación de error de conexión
            snack_sin_internet = ft.SnackBar(
                content=ft.Text("No hay conexión a internet, inténtelo más tarde"),
                bgcolor=ft.Colors.RED_600,
                open=True,
            )
            page.overlay.append(snack_sin_internet)
            page.update()
        else:
            capa_modal.visible = False
            input_correo_recuperar.value = ""
            error_recuperar.visible = False
            

            # Notificación de éxito
            snack = ft.SnackBar(
                content=ft.Text(f"Correo de recuperación enviado a: {correo}"),
                bgcolor=ft.Colors.GREEN_600,
                open = True,
            )
            page.overlay.append(snack)
            page.update()

        input_correo_recuperar.update()
        error_recuperar.update()

    # Contenido de la tarjeta del modal
    tarjeta_modal_contenido = ft.Container(
        width=550,
        bgcolor=c["bg_card_white"],
        border_radius=24,
        padding=ft.Padding.all(25),
        content=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Botón Flecha Atrás para cerrar
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            icon_size=20,
                            bgcolor=COLOR_BOTON_MODAL,
                            on_click=cerrar_modal,
                        ),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                "Recuperar contraseña",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_TITULO_MODAL,
                            ),
                        ),
                        ft.Container(width=40),
                    ],
                ),
                ft.Text(
                    "Ingresa los datos:",
                    size=18,
                    color=COLOR_SUBTITULO_MODAL,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=5),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Correo electrónico",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_LABEL_MODAL,
                        ),
                        input_correo_recuperar,
                        error_recuperar,
                    ],
                ),
                ft.Container(height=5),
                ft.Text(
                    "Se enviará un correo electrónico a tu bandeja\nde entrada para cambiar la contraseña",
                    size=16,
                    color=c["texto_secundario"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    margin=ft.Margin.symmetric(vertical=5),
                    content=ft.Text(
                        "- - " * 22,
                        color=COLOR_INPUT_BORDER_MODAL,
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                    ),
                ),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Enviar correo",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                        size=18,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_BOTON_MODAL,
                        shape=ft.RoundedRectangleBorder(radius=30),
                        elevation=0,
                    ),
                    width=float("inf"),
                    height=42,
                    on_click=enviar_correo_recuperacion,
                ),
            ],
        ),
    )

    # Asignamos la tarjeta dentro de la capa sombreada
    capa_modal.content = tarjeta_modal_contenido

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
            error_usuario.value = "El correo o número telefónico es obligatorio"
            error_usuario.visible = True
            input_usuario.border_color = COLOR_ERROR
            es_valido = False
        elif " " in val_user:
            error_usuario.value = "No puedes dejar espacios al ingresar un correo"
            error_usuario.visible = True
            input_usuario.border_color = COLOR_ERROR
            es_valido = False
        elif "@" not in val_user:
            error_usuario.value = "Es necesario colocar un @ en el correo"
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
            # --- Compara contra el correo y contraseña guardados en Ajustes ---
            usuario = UsuarioDAO.login(val_user, val_pass)
            if usuario:
                error_usuario.visible = False
                error_usuario.update()
                if on_login_exitoso:
                    on_login_exitoso(usuario)
            else:
                error_password.visible = True
                error_password.update()


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

    return pantalla_completa


if __name__ == "__main__":
    # Esto solo se ejecuta si corres login_view.py directamente (para probarlo aislado)
    def _prueba(page: ft.Page):
        page.add(vista_login(page))

    ft.app(target=_prueba, assets_dir="assets") 