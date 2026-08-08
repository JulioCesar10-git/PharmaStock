import flet as ft
from datetime import datetime

from frontend.theme import colores
from frontend.state import ESTADO_UI
from frontend.navegacion import nav_item, actualizar_avisos_nav
from frontend.alertas_inventario import contar_avisos_inventario, obtener_avisos_inventario
from frontend.components.recordatorios import crear_modulo_recordatorios
from frontend.views.general import vista_general
from frontend.views.inventario import vista_inventario
from frontend.views.empleados import vista_empleados
from frontend.views.reportes import vista_reportes
from frontend.views.proveedores import vista_proveedores
from frontend.views.ajustes import vista_ajustes
from frontend.login_view import vista_login

def main_window(page: ft.Page):
    # --- Configuración base de la página ---
    page.title = "PharmaStock"
    page.window.width = 1100
    page.window.height = 700
    page.padding = 0

    page.fonts = {
        "Poppins": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Regular.ttf",
        "Poppins-Bold": "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Bold.ttf",
    }
    page.theme = ft.Theme(font_family="Poppins")
    page.dark_theme = ft.Theme(font_family="Poppins")

    # --- Estado inicial compartido entre pestañas ---
    fecha_hoy = datetime.now()
    fecha_activa = {
        "dia": fecha_hoy.day,
        "mes": fecha_hoy.month,
        "año": fecha_hoy.year,
    }
    modulo_recordatorios = crear_modulo_recordatorios(page, fecha_activa)
    estado_navegacion = {"seccion_actual": "General"}

    # --- Diálogo: centro de notificaciones ---
    def abrir_modal_notificaciones(e):
        c = colores()
        modo_oscuro = ESTADO_UI["modo_oscuro"]

        # --- Azul marino: mismo color de fondo que usa la barra de navegación lateral ---
        AZUL_LATERAL = c["fondo_menu"]

        avisos_inventario = obtener_avisos_inventario()

        # --- Lista de avisos dentro del diálogo (mismas alertas que la
        #     tarjeta "AVISOS Y ALERTAS" de la pestaña General) ---
        controls_avisos = []
        if not avisos_inventario:
            controls_avisos.append(
                ft.Text(
                    "No hay alertas de stock o caducidad registradas.",
                    color=ft.Colors.WHITE if modo_oscuro else c["texto_secundario"],
                    size=13,
                )
            )
        else:
            for aviso in avisos_inventario:
                tipo = aviso["tipo"]
                if tipo == "Caducado":
                    color_texto = c["text_red"]
                    bg_pildora = c["pildora_caducado"]
                elif tipo == "Por caducar":
                    color_texto = "#E65100"
                    bg_pildora = c["pildora_por_caducar"]
                else:
                    color_texto = "#B71C1C"
                    bg_pildora = c["pildora_stock_bajo"]

                # --- En modo oscuro, todos los textos de la tarjeta se ven en blanco ---
                if modo_oscuro:
                    color_texto = ft.Colors.WHITE

                controls_avisos.append(
                    ft.Container(
                        bgcolor=bg_pildora,
                        padding=10,
                        border_radius=8,
                        content=ft.Column(
                            [
                                ft.Row([
                                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=color_texto, size=18),
                                    ft.Text(f"{tipo}: {aviso['nombre']}", color=color_texto, size=13, weight=ft.FontWeight.BOLD, expand=True),
                                ], spacing=8),
                                ft.Text(aviso["detalle"], color=color_texto, size=11),
                            ],
                            spacing=4,
                        ),
                    )
                )

        # --- Construcción del AlertDialog ---
        dlg = ft.AlertDialog(
            bgcolor=AZUL_LATERAL if modo_oscuro else c["bg_card_white"],
            title=ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.WHITE if modo_oscuro else c["azul_card"]),
                ft.Text(
                    "Centro de Notificaciones",
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if modo_oscuro else c["input_bg"],
                    size=16,
                )
            ], spacing=8),
            content=ft.Container(
                width=400,
                height=300,
                content=ft.ListView(controls=controls_avisos, spacing=8, expand=True)
            ),
            actions=[],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # --- Cierre del diálogo ---
        def cerrar_dialogo(e_cerrar):
            dlg.open = False
            page.update()

        dlg.actions = [
            ft.TextButton(
                "Cerrar",
                on_click=cerrar_dialogo,
                style=ft.ButtonStyle(color=ft.Colors.WHITE) if modo_oscuro else None,
            )
        ]

        if dlg not in page.overlay:
            page.overlay.append(dlg)

        dlg.open = True
        page.update()

    # --- Constantes del menú de navegación ---
    ORDEN_SECCIONES_PRINCIPALES = ["General", "Inventario", "Empleados", "Reportes", "Proveedores"]
    ALTO_ITEM_NAV = 48
    ESPACIO_ITEM_NAV = 8

    def construir_interfaz():
        # --- Construye/reconstruye toda la interfaz (se llama al iniciar y al cambiar tema) ---
        c = colores()
        page.bgcolor = c["fondo_app"]

        nav_items_refs = []

        def refrescar_avisos_inventario():
            actualizar_avisos_nav(nav_items_refs, "Inventario", contar_avisos_inventario(), page)

        indice_inicial = (
            ORDEN_SECCIONES_PRINCIPALES.index(estado_navegacion["seccion_actual"])
            if estado_navegacion["seccion_actual"] in ORDEN_SECCIONES_PRINCIPALES
            else 0
        )
        # --- Píldora flotante que resalta la sección activa del menú ---
        pildora_nav = ft.Container(
            width=200,
            height=ALTO_ITEM_NAV,
            bgcolor="#588CEF",
            border_radius=30,
            shadow=ft.BoxShadow(
                blur_radius=5,
                spread_radius=1,
                color="#A9B8CE",
                offset=ft.Offset(0, 0),
            ),
            top=indice_inicial * (ALTO_ITEM_NAV + ESPACIO_ITEM_NAV),
            left=0,
            opacity=1 if estado_navegacion["seccion_actual"] in ORDEN_SECCIONES_PRINCIPALES else 0,
            animate_position=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        # --- Título dinámico de la sección actual (arriba del contenido) ---
        titulo_seccion_text = ft.Row(
            controls=[
                ft.Text(estado_navegacion["seccion_actual"], size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- Manejador de clic: cambia de sección y refresca la vista dinámica ---
        def cambiar_seccion(e_o_nombre):
            if isinstance(e_o_nombre, str):
                key_clickeado = e_o_nombre
            else:
                key_clickeado = e_o_nombre.control.data

            estado_navegacion["seccion_actual"] = key_clickeado

            if key_clickeado in ORDEN_SECCIONES_PRINCIPALES:
                pildora_nav.top = ORDEN_SECCIONES_PRINCIPALES.index(key_clickeado) * (ALTO_ITEM_NAV + ESPACIO_ITEM_NAV)
                pildora_nav.opacity = 1
            else:
                pildora_nav.opacity = 0

            for ref in nav_items_refs:
                activo = ref["key"] == key_clickeado
                if ref["key"] not in ORDEN_SECCIONES_PRINCIPALES:
                    ref["container"].bgcolor = "#588CEF" if activo else None
                    ref["container"].shadow = ft.BoxShadow(
                        blur_radius=5,
                        spread_radius=1,
                        color="#A9B8CE",
                        offset=ft.Offset(0, 0)
                    ) if activo else None
                ref["icono"].color = ft.Colors.WHITE if activo else c["texto_nav_inactivo"]
                ref["texto"].color = ft.Colors.WHITE if activo else c["texto_nav_inactivo"]

            if key_clickeado == "General":
                area_dinamica.content = vista_general(page, fecha_activa, modulo_recordatorios, cambiar_seccion)
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]
            elif key_clickeado == "Inventario":
                area_dinamica.content = vista_inventario(page, modulo_recordatorios, on_inventario_actualizado=refrescar_avisos_inventario)
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]
            elif key_clickeado == "Empleados":
                area_dinamica.content = vista_empleados(page)
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]
            elif key_clickeado == "Reportes":
                area_dinamica.content = vista_reportes(page)
                titulo_seccion_text.controls = [
                    ft.Text("Ventas", size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                    ft.Text("|", size=20, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                    ft.Text("Consumo Promedio Mensual", size=16, color=c["texto_secundario"], weight=ft.FontWeight.W_500),
                ]
            elif key_clickeado == "Proveedores":
                area_dinamica.content = vista_proveedores(page)
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]
            elif key_clickeado == "Ajustes":
                area_dinamica.content = vista_ajustes(page, construir_interfaz)
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]
            else:
                area_dinamica.content = ft.Text(f"Contenido de {key_clickeado}", size=18, color=c["azul_card"])
                titulo_seccion_text.controls = [
                    ft.Text(key_clickeado, size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                ]

            page.update()

        # --- Barra superior: título de sección + iconos de notificaciones/ajustes ---
        top_bar = ft.Container(
            padding=ft.Padding.only(left=30, top=15, right=30, bottom=15),
            bgcolor=c["fondo_menu"],
            content=ft.Row(
                [
                    titulo_seccion_text,
                    ft.Row(
                        [
                            ft.Container(
                                width=36,
                                height=36,
                                border_radius=18,
                                bgcolor=ft.Colors.WHITE,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=c["azul_card"], size=20),
                                on_click=abrir_modal_notificaciones,
                                ink=True,
                                tooltip="Notificaciones",
                            ),
                            ft.Container(
                                width=36,
                                height=36,
                                border_radius=18,
                                bgcolor=c["avatar_bg"],
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.PERSON_OUTLINED, color=ft.Colors.WHITE, size=20),
                                data="Ajustes",
                                on_click=cambiar_seccion,
                                ink=True,
                                tooltip="Ajustes",
                            ),
                        ],
                        spacing=10
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # --- Menú lateral: logo, ítems de navegación y botón de ajustes ---
        menu_lateral = ft.Container(
            width=250,
            bgcolor=c["fondo_menu"],
            padding=10,
            content=ft.Column(
                [
                    ft.Row(
                        controls=[
                            ft.Image(
                                src="PharmaStock_LogoOscuro_3.png" if ESTADO_UI["modo_oscuro"] else "PharmaStock_SinFondo.png",
                                width=60,
                                height=60,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                            ft.Container(
                                margin=ft.Margin.only(left=-5),
                                content=ft.Image(
                                    src="PharmaStock_LogoOscuro_4.png" if ESTADO_UI["modo_oscuro"] else "Logo_PharmaStockCompleto_SinFondo(Letras).png",
                                    width=170,
                                    height=40,
                                    fit=ft.BoxFit.CONTAIN,
                                    error_content=ft.Text("PHARMASTOCK", size=18, weight=ft.FontWeight.BOLD, color=c["azul_card"]),
                                ),
                            ),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(color=ft.Colors.BLUE_GREY_100),
                    ft.Stack(
                        controls=[
                            pildora_nav,
                            ft.Column(
                                [
                                    nav_item(ft.Icons.HOME, "General", "General", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                                              activo=(estado_navegacion["seccion_actual"] == "General"), color_burbuja="#588CEF",
                                              fondo_propio=False, height=ALTO_ITEM_NAV),
                                    nav_item(ft.Icons.INVENTORY_2, "Inventario", "Inventario", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                                              activo=(estado_navegacion["seccion_actual"] == "Inventario"), color_burbuja="#588CEF",
                                              fondo_propio=False, height=ALTO_ITEM_NAV, avisos=contar_avisos_inventario()),
                                    nav_item(ft.Icons.PEOPLE, "Empleados", "Empleados", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                                              activo=(estado_navegacion["seccion_actual"] == "Empleados"), color_burbuja="#588CEF",
                                              fondo_propio=False, height=ALTO_ITEM_NAV),
                                    nav_item(ft.Icons.ATTACH_MONEY, "Ventas", "Reportes", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                                              activo=(estado_navegacion["seccion_actual"] == "Reportes"), color_burbuja="#588CEF",
                                              fondo_propio=False, height=ALTO_ITEM_NAV),
                                    nav_item(ft.Icons.LOCAL_SHIPPING, "Proveedores", "Proveedores", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                                              activo=(estado_navegacion["seccion_actual"] == "Proveedores"), color_burbuja="#588CEF",
                                              fondo_propio=False, height=ALTO_ITEM_NAV),
                                ],
                                spacing=ESPACIO_ITEM_NAV,
                            ),
                        ],
                    ),
                    ft.Container(expand=True),
                    nav_item(ft.Icons.SETTINGS, "Ajustes", "Ajustes", cambiar_seccion, nav_items_refs, c["texto_nav_inactivo"],
                              activo=(estado_navegacion["seccion_actual"] == "Ajustes"), color_burbuja="#588CEF"),
                ]
            ),
        )

        # --- Contenido inicial según la sección activa al construir la interfaz ---
        if estado_navegacion["seccion_actual"] == "Inventario":
            contenido_inicial = vista_inventario(page, modulo_recordatorios, on_inventario_actualizado=refrescar_avisos_inventario)
        elif estado_navegacion["seccion_actual"] == "Empleados":
            contenido_inicial = vista_empleados(page)
        elif estado_navegacion["seccion_actual"] == "Reportes":
            contenido_inicial = vista_reportes(page)
            titulo_seccion_text.controls = [
                ft.Text("Ventas", size=24, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                ft.Text("|", size=20, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                ft.Text("Consumo Promedio Mensual", size=16, color=c["texto_secundario"], weight=ft.FontWeight.W_500),
            ]
        elif estado_navegacion["seccion_actual"] == "Proveedores":
            contenido_inicial = vista_proveedores(page)
        elif estado_navegacion["seccion_actual"] == "Ajustes":
            contenido_inicial = vista_ajustes(page, construir_interfaz)
        else:
            contenido_inicial = vista_general(page, fecha_activa, modulo_recordatorios, cambiar_seccion)

        # --- Contenedor de la vista dinámica (cambia según la sección) ---
        area_dinamica = ft.Container(
            content=contenido_inicial,
            padding=20,
            expand=True,
            bgcolor=c["fondo_lienzo"],
        )

        # --- Ensamblado final: barra superior + área dinámica, junto al menú lateral ---
        contenido_principal = ft.Column([top_bar, area_dinamica], spacing=0, expand=True)

        page.controls.clear()
        page.add(ft.Row([menu_lateral, contenido_principal], expand=True, spacing=0))
        page.update()

    def on_login_exitoso(usuario):
        print(f"✅ Bienvenido {usuario.usuario_usuario}")

        # Aquí después navegamos a la ventana principal
        estado_navegacion["seccion_actual"] = "General"
        page.controls.clear()
        construir_interfaz()

    page.controls.clear()
    page.add(vista_login(page, on_login_exitoso=on_login_exitoso))
    page.update()
    

ft.app(target=main_window, assets_dir="frontend/assets")