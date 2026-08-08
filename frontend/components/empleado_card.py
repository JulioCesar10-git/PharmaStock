import flet as ft

from theme import colores
from state import ESTADO_UI

def crear_tarjeta_empleado(empleado, on_editar=None, on_eliminar=None):
    c = colores()

    nombre = empleado.get("nombre", "Sin nombre")
    puesto = empleado.get("puesto", "Sin puesto")
    color_borde = empleado.get("color_borde", c["borde_campo"])
    numero = empleado.get("numero", None)
    imagen_empleado = empleado.get("imagen")

    # --- En modo oscuro, el número y los íconos de editar/eliminar se ven en blanco ---
    modo_oscuro = ESTADO_UI["modo_oscuro"]
    color_icono_editar = "#FFFFFF" if modo_oscuro else "#1E88E5"
    color_icono_eliminar = "#FFFFFF" if modo_oscuro else "#E53935"
    color_texto_numero = "#FFFFFF" if modo_oscuro else c["azul_card"]

    # --- Botones de editar/eliminar y número, visibles solo en hover ---
    botones_accion = ft.Container(
        opacity=0.0,
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        bottom=-4, left=-0.75, right=-0.75,
        padding=ft.Padding.symmetric(horizontal=0, vertical=4),
        content=ft.Row(
            [

                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=15, color=color_icono_editar),
                    bgcolor=c["bg_card_white"],
                    shape=ft.BoxShape.CIRCLE,
                    padding=6,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=3,
                        color=c["bg_card_white"],
                        offset=ft.Offset(0, 2)
                    ),
                    on_click=lambda e: on_editar(empleado) if on_editar else None,
                ),

                ft.Container(
                    bgcolor=c["bg_card_white"],
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=8,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#00000020",
                        offset=ft.Offset(0, 2)
                    ),
                    content=ft.Text(
                        f"# {numero:02d}" if numero is not None else "",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=color_texto_numero,
                    ),
                ),

                ft.Container(
                    content=ft.Icon(ft.Icons.DELETE_OUTLINED, size=15, color=color_icono_eliminar),
                    bgcolor=c["bg_card_white"],
                    shape=ft.BoxShape.CIRCLE,
                    padding=6,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=3,
                        color=c["bg_card_white"],
                        offset=ft.Offset(0, 2)
                    ),
                    on_click=lambda e: on_eliminar(empleado) if on_eliminar else None,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )

    # --- Avatar: muestra la imagen del empleado si existe, o el ícono por defecto ---
    TAMANO_AVATAR_NORMAL = 58
    TAMANO_AVATAR_HOVER = 90

    if imagen_empleado:
        avatar = ft.Container(
            width=TAMANO_AVATAR_NORMAL,
            height=TAMANO_AVATAR_NORMAL,
            border_radius=14,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=ft.Image(src=imagen_empleado, fit=ft.BoxFit.COVER, expand=True),
        )
    else:
        avatar = ft.Container(
            width=TAMANO_AVATAR_NORMAL,
            height=TAMANO_AVATAR_NORMAL,
            border_radius=14,
            bgcolor=c["avatar_bg"],
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=38),
        )

    # --- Capa con avatar, nombre y puesto del empleado ---
    capa_texto = ft.Container(
        padding=ft.Padding.only(left=10, right=10, bottom=40),
        alignment=ft.Alignment.TOP_CENTER,
        content=ft.Column(
            [
                avatar,
                ft.Text(nombre, weight=ft.FontWeight.BOLD, color=c["input_bg"], size=13, text_align=ft.TextAlign.CENTER),
                ft.Text(puesto, size=11, color="#FFFFFF" if modo_oscuro else c["boton_secundario"], text_align=ft.TextAlign.CENTER),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # --- Efecto hover: resalta la tarjeta y muestra los botones de acción ---
    def al_pasar_mouse(e):
        esta_hover = str(e.data).lower() in ["true", "1"]

        if esta_hover:
            e.control.scale = 1.05
            e.control.shadow = ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color="#A9B8CE",
                offset=ft.Offset(0, 3),
            )
            e.control.height = ALTURA_TARJETA_HOVER
            avatar.width = TAMANO_AVATAR_HOVER
            avatar.height = TAMANO_AVATAR_HOVER
            botones_accion.opacity = 1.0
        else:
            e.control.scale = 1.0
            e.control.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color="#00000015",
                offset=ft.Offset(0, 2)
            )
            e.control.height = ALTURA_TARJETA_NORMAL
            avatar.width = TAMANO_AVATAR_NORMAL
            avatar.height = TAMANO_AVATAR_NORMAL
            botones_accion.opacity = 0.0

        e.control.update()
        avatar.update()
        botones_accion.update()

    # --- Tarjeta principal (avatar/texto + botones superpuestos) ---
    ALTURA_TARJETA_NORMAL = 170
    ALTURA_TARJETA_HOVER = 205

    tarjeta = ft.Container(
        width=140,
        height=ALTURA_TARJETA_NORMAL,
        margin=ft.Margin.all(8),
        bgcolor=c["bg_card_blue"],
        border=ft.Border.all(3, color_borde),
        border_radius=14,
        padding=ft.Padding.only(top=15, bottom=8),
        scale=1.0,
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000015", offset=ft.Offset(0, 2)),
        on_hover=al_pasar_mouse,
        on_click=lambda e: None,
        content=ft.Stack(
            controls=[
                capa_texto,
                botones_accion,
            ],
            expand=True
        ),
    )

    return tarjeta