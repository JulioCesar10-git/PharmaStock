from datetime import datetime

import flet as ft

from theme import colores

def crear_tarjeta_producto(producto, on_editar=None, on_eliminar=None):
    c = colores()

    nombre = producto.get("nombre", "Sin nombre")
    tipo = producto.get("tipo", "Producto")
    precio = producto.get("precio", 0.0)
    stock = producto.get("stock", 0)
    caducidad = producto.get("caducidad", "N/A")
    alertas = producto.get("alertas", [])

    # --- Calcula las alertas activas (stock bajo / por caducar / caducado) ---
    alertas_locales = list(alertas) if alertas else []

    if stock <= 50 and "Stock bajo" not in alertas_locales:
        alertas_locales.insert(0, "Stock bajo")

    if caducidad and caducidad != "N/A":
        try:
            fecha_cad = datetime.strptime(caducidad, "%m/%Y")
            hoy = datetime.now()
            diferencia_meses = (fecha_cad.year - hoy.year) * 12 + (fecha_cad.month - hoy.month)

            if diferencia_meses < 0:
                if "Caducado" not in alertas_locales:
                    alertas_locales.append("Caducado")
                if "Por caducar" in alertas_locales:
                    alertas_locales.remove("Por caducar")
            elif 0 <= diferencia_meses <= 3:
                if "Por caducar" not in alertas_locales:
                    alertas_locales.append("Por caducar")
                if "Caducado" in alertas_locales:
                    alertas_locales.remove("Caducado")
            else:
                if "Por caducar" in alertas_locales:
                    alertas_locales.remove("Por caducar")
                if "Caducado" in alertas_locales:
                    alertas_locales.remove("Caducado")
        except ValueError:
            pass

    # --- Imagen del producto (o placeholder si no tiene una asignada) ---
    ruta_imagen = producto.get("imagen")

    ALTURA_IMG_NORMAL = 95
    ALTURA_IMG_HOVER = 150

    if ruta_imagen:
        imagen_placeholder = ft.Container(
            height=ALTURA_IMG_NORMAL,
            border_radius=ft.BorderRadius.only(top_left=10, top_right=10),
            border=ft.Border.all(1, c["borde_campo"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC),
            content=ft.Image(
                src=ruta_imagen,
                fit=ft.BoxFit.COVER,
                width=float("inf"),
                expand=True,
            ),
        )
    else:
        imagen_placeholder = ft.Container(
            height=ALTURA_IMG_NORMAL,
            bgcolor=c["fondo_lienzo"],
            border_radius=ft.BorderRadius.only(top_left=10, top_right=10),
            border=ft.Border.all(1, c["borde_campo"]),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC),
            content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color=c["borde_campo"], size=32),
            alignment=ft.Alignment(0, 0),
        )

    # --- Botones de editar/eliminar, visibles solo en hover ---
    botones_accion = ft.Container(
        opacity=0.0,
        animate_opacity=200,
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=14, color="#1E88E5"),
                    bgcolor=ft.Colors.WHITE,
                    shape=ft.BoxShape.CIRCLE,
                    padding=6,
                    shadow=ft.BoxShadow(blur_radius=4, color="#00000020"),
                    on_click=lambda e: on_editar(producto) if on_editar else None,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.DELETE_OUTLINED, size=14, color="#E53935"),
                    bgcolor=ft.Colors.WHITE,
                    shape=ft.BoxShape.CIRCLE,
                    padding=6,
                    shadow=ft.BoxShadow(blur_radius=4, color="#00000020"),
                    on_click=lambda e: on_eliminar(producto) if on_eliminar else None,
                ),
            ],
            spacing=4,
        ),
    )

    # --- Píldoras de alertas (esquina superior de la imagen) ---
    alertas_column = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text(alerta, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                bgcolor="#B71C1C" if alerta == "Caducado" else c["text_red"],
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=12,
            )
            for alerta in alertas_locales
        ],
        spacing=4,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    # --- Encabezado: imagen + alertas + botones superpuestos ---
    header_stack = ft.Stack(
        controls=[
            imagen_placeholder,
            ft.Container(content=alertas_column, top=6, right=6),
            ft.Container(content=botones_accion, bottom=6, right=6),
        ]
    )

    tiene_alerta_fecha = "Por caducar" in alertas_locales or "Caducado" in alertas_locales

    # --- Información del producto: categoría, precio, nombre, stock y caducidad ---
    info_container = ft.Container(
        padding=8,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(tipo, size=11, color="#FFFFFF", weight=ft.FontWeight.W_500),
                            bgcolor=c["boton_secundario"],
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            border_radius=12,
                        ),
                        ft.Text(f"${precio}", size=11, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    nombre,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=c["input_bg"],
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(f"En almacén: {stock} pz", size=12, color=c["texto_secundario"]),
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CALENDAR_TODAY_OUTLINED,
                            size=11,
                            color=c["text_red"] if tiene_alerta_fecha else c["texto_secundario"],
                        ),
                        ft.Text(
                            f"Caducidad: {caducidad}",
                            size=10,
                            weight=ft.FontWeight.W_500 if tiene_alerta_fecha else ft.FontWeight.NORMAL,
                            color=c["text_red"] if tiene_alerta_fecha else c["texto_secundario"],
                        ),
                    ],
                    spacing=3,
                ),
            ],
            spacing=3,
        ),
    )

    # --- Tarjeta interior (encabezado + info) ---
    tarjeta_interior = ft.Container(
        bgcolor=c["bg_card_white"],
        border_radius=12,
        content=ft.Column([header_stack, info_container], spacing=0),
    )

    # --- Gradientes del borde según hover ---
    gradiente_inactivo = ft.LinearGradient(
        colors=["#00000000", "#00000000"],
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
    )
    gradiente_activo = ft.LinearGradient(
        colors=["#5F9CFF", "#1D4ED8", "#4338CA"],
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
    )

    # --- Tarjeta externa con borde en gradiente ---
    tarjeta_externa = ft.Container(
        padding=2.5,
        border_radius=14,
        gradient=gradiente_inactivo,
        scale=1.0,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)),
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=tarjeta_interior,
        on_click=lambda e: None,
    )

    # --- Efecto hover: resalta el borde y muestra los botones de acción ---
    def al_pasar_mouse(e):
        esta_hover = str(e.data).lower() in ["true", "1"]

        if esta_hover:
            tarjeta_externa.scale = 1.04
            tarjeta_externa.gradient = gradiente_activo
            tarjeta_externa.shadow = ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color="#A9B8CE",
                offset=ft.Offset(0, 3),
            )
            imagen_placeholder.height = ALTURA_IMG_HOVER
            botones_accion.opacity = 1.0
        else:
            tarjeta_externa.scale = 1.0
            tarjeta_externa.gradient = gradiente_inactivo
            tarjeta_externa.shadow = ft.BoxShadow(
                spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)
            )
            imagen_placeholder.height = ALTURA_IMG_NORMAL
            botones_accion.opacity = 0.0

        tarjeta_externa.update()

    tarjeta_externa.on_hover = al_pasar_mouse

    return tarjeta_externa