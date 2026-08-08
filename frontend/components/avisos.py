import flet as ft
from theme import colores
from state import PRODUCTOS_GLOBALES, obtener_estado_caducidad

# --- Tarjeta individual de un aviso (stock bajo / por caducar / caducado) ---
def crear_item_aviso_alerta(nombre, tipo_alerta, detalle, on_click_callback=None):
    c = colores()

    # --- Color de texto: blanco en toda la tarjeta ---
    color_texto = c["input_bg"]

    # --- Color de la píldora de fondo, según el tipo de alerta ---
    if tipo_alerta == "Caducado":
        bg_pildora = c["pildora_caducado"]
    elif tipo_alerta == "Por caducar":
        bg_pildora = c["pildora_por_caducar"]
    else:
        bg_pildora = c["pildora_stock_bajo"]

    # --- Sin sombra: las tarjetitas de aviso ya no llevan shadow ---
    sombra_normal = None
    sombra_hover = None

    tarjeta_aviso = ft.Container(
        bgcolor=c["bg_card_white"],
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        shadow=sombra_normal,
        offset=ft.Offset(0, 0),
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_offset=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
        ink=True,
        on_click=on_click_callback,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Alerta: {tipo_alerta}", color=color_texto, weight=ft.FontWeight.W_500, size=11),
                        ft.Container(expand=True),
                        ft.Text(detalle, size=10, color=color_texto, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(nombre, size=10, color=color_texto, weight=ft.FontWeight.BOLD),
                            bgcolor=bg_pildora,
                            padding=ft.Padding.symmetric(horizontal=5, vertical=3),
                            border_radius=5,
                            expand=True,
                        ),
                    ]
                ),
            ],
            spacing=4,
        ),
    )

    # --- Efecto hover: la tarjeta "se levanta" con un pequeño desplazamiento
    #     vertical (no ensancha la tarjeta, así no se recorta por los lados) ---
    def al_pasar_mouse(e):
        esta_hover = str(e.data).lower() in ["true", "1"]

        if esta_hover:
            tarjeta_aviso.offset = ft.Offset(0, -0.04)
            tarjeta_aviso.shadow = sombra_hover
        else:
            tarjeta_aviso.offset = ft.Offset(0, 0)
            tarjeta_aviso.shadow = sombra_normal

        tarjeta_aviso.update()

    tarjeta_aviso.on_hover = al_pasar_mouse

    return tarjeta_aviso

def crear_tarjeta_avisos(cambiar_pestana_callback=None):
    c = colores()

    # --- Columna con scroll donde se listan los avisos ---
    columna_avisos = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
        spacing=8,
    )

    # --- Envoltorio con padding: da "aire" alrededor de las tarjetitas para que
    #     su sombra y su escala en hover no se corten con el borde del recuadro ---
    contenedor_avisos = ft.Container(
        content=columna_avisos,
        padding=ft.Padding(left=5, right=8, top=5, bottom=8),
        expand=True,
    )

    # --- Recorre los productos y genera un aviso por cada alerta activa ---
    def actualizar_avisos():
        columna_avisos.controls.clear()
        avisos_generados = 0

        for prod in PRODUCTOS_GLOBALES:
            nombre = prod.get("nombre", "Producto")
            stock = prod.get("stock", 0)
            caducidad = prod.get("caducidad", "N/A")

            def ir_a_inventario_con_filtro(e, nombre_prod=nombre):
                if cambiar_pestana_callback:

                    cambiar_pestana_callback("Inventario")

            if stock <= 50:
                columna_avisos.controls.append(
                    crear_item_aviso_alerta(nombre, "Stock bajo", f"Stock: {stock} pz", on_click_callback=ir_a_inventario_con_filtro)
                )
                avisos_generados += 1

            estado_cad = obtener_estado_caducidad(caducidad)
            if estado_cad == "Caducado":
                columna_avisos.controls.append(
                    crear_item_aviso_alerta(nombre, "Caducado", f"Cad: {caducidad}", on_click_callback=ir_a_inventario_con_filtro)
                )
                avisos_generados += 1
            elif estado_cad == "Por caducar":
                columna_avisos.controls.append(
                    crear_item_aviso_alerta(nombre, "Por caducar", f"Cad: {caducidad}", on_click_callback=ir_a_inventario_con_filtro)
                )
                avisos_generados += 1

        if avisos_generados == 0:
            columna_avisos.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text("No hay alertas de stock o caducidad registradas.", size=12, color=c["text_red"])
                )
            )

    actualizar_avisos()

    # --- Tarjeta contenedora con encabezado "AVISOS Y ALERTAS" ---
    return ft.Container(
        bgcolor=c["bg_card_yellow"],
        border_radius=20,
        padding=10,
        expand=True,
        shadow=None,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=c["titulo_avisos"], size=20),
                        ft.Text("AVISOS Y ALERTAS", weight=ft.FontWeight.BOLD, color=c["titulo_avisos"], size=14),
                    ],
                    spacing=8,
                ),
                contenedor_avisos,
            ]
        ),
    )