import flet as ft

def nav_item(icon, texto, key, on_click, nav_items_refs, color_activo, activo=False, color_burbuja=None,
             fondo_propio=True, height=None, avisos=0, color_avisos="#E53935"):
    # --- Controles de icono y texto según estado activo/inactivo ---
    color_burbuja = color_burbuja or color_activo

    icono_ctrl = ft.Icon(icon, color=ft.Colors.WHITE if activo else color_activo, size=22)
    texto_ctrl = ft.Text(
        texto,
        color=ft.Colors.WHITE if activo else color_activo,
        weight=ft.FontWeight.BOLD if activo else ft.FontWeight.W_500,
    )

    # --- Contenedor principal del ítem de navegación ---
    item = ft.Container(
        content=ft.Row([icono_ctrl, texto_ctrl], spacing=10),
        bgcolor=(color_burbuja if activo else None) if fondo_propio else None,

        shadow=ft.BoxShadow(
            blur_radius=5,
            spread_radius=1,
            color="#A9B8CE",
            offset=ft.Offset(0, 0)
        ) if (activo and fondo_propio) else None,

        animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT) if fondo_propio else None,

        border_radius=30,
        padding=ft.Padding(left=15, top=12, right=15, bottom=12),
        width=200,
        height=height,
        data=key,
        on_click=on_click,
        ink=True,
    )

    # --- Burbuja numérica de avisos pendientes ---
    texto_avisos = str(avisos) if avisos <= 99 else "99+"
    avisos_texto_ctrl = ft.Text(
        texto_avisos,
        size=11,
        color=ft.Colors.WHITE,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )
    avisos_container = ft.Container(
        content=avisos_texto_ctrl,
        width=20,
        height=20,
        bgcolor=color_avisos,
        border_radius=100,
        alignment=ft.Alignment.CENTER,
        top=14,
        right=12,
        visible=avisos > 0,
        shadow=ft.BoxShadow(blur_radius=4, spread_radius=0, color="#00000040", offset=ft.Offset(0, 1)),
    )

    # --- Stack: superpone la burbuja de avisos sobre el ítem ---
    item_con_avisos = ft.Stack(controls=[item, avisos_container])

    # --- Registro del ítem para poder actualizarlo después ---
    nav_items_refs.append({
        "container": item,
        "icono": icono_ctrl,
        "texto": texto_ctrl,
        "key": key,
        "avisos_texto": avisos_texto_ctrl,
        "avisos_container": avisos_container,
    })
    return item_con_avisos

def actualizar_avisos_nav(nav_items_refs, key, nuevo_valor, page=None):
    # --- Busca el ítem por su key y actualiza su burbuja de avisos ---
    for ref in nav_items_refs:
        if ref["key"] != key:
            continue
        texto_mostrado = str(nuevo_valor) if nuevo_valor <= 99 else "99+"
        ref["avisos_texto"].value = texto_mostrado
        ref["avisos_container"].visible = nuevo_valor > 0
        break

    if page is not None:
        page.update()