import flet as ft

def main_window(page: ft.Page):
    page.title = "PharmaStock"
    page.window_width = 1100
    page.window_height = 700
    page.padding = 0

    nav_items_refs = []
    
    def nav_item(icon, texto, key, activo=False, badge=None):
        icono_ctrl = ft.Icon(icon, color=ft.Colors.WHITE if activo else ft.Colors.BLUE_700, size=20)
        texto_ctrl = ft.Text(
            texto,
            color=ft.Colors.WHITE if activo else ft.Colors.BLUE_700,
            weight=ft.FontWeight.BOLD if activo else ft.FontWeight.W_500,
        )

        contenido_row = ft.Row(
            controls=[icono_ctrl, texto_ctrl],
            spacing=10,
        )

        if badge:
            contenido_row.controls.append(
                ft.Container(
                    content=ft.Text(str(badge), size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.RED_400,
                    width=22,
                    height=22,
                    border_radius=11,
                    alignment=ft.Alignment.CENTER,
                )
            )
            contenido_row.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        else:
            contenido_row.alignment = ft.MainAxisAlignment.START

        item = ft.Container(
            content=contenido_row,
            bgcolor=ft.Colors.BLUE_100 if activo else None,
            border_radius=30,
            padding=ft.Padding(left=15, top=12, right=15, bottom=12),
            width=200,
            data=key,           
            on_click=cambiar_seccion,
            ink=True,           
        )

        nav_items_refs.append({
            "container": item,
            "icono": icono_ctrl,
            "texto": texto_ctrl,
            "key": key,
        })

        return item

    def cambiar_seccion(e):
        key_clickeado = e.control.data

        for ref in nav_items_refs:
            activo = ref["key"] == key_clickeado
            ref["container"].bgcolor = ft.Colors.BLUE_100 if activo else None
            ref["icono"].color = ft.Colors.WHITE if activo else ft.Colors.BLUE_700
            ref["texto"].color = ft.Colors.WHITE if activo else ft.Colors.BLUE_700
            ref["texto"].weight = ft.FontWeight.BOLD if activo else ft.FontWeight.W_500

        
        contenido.content = ft.Column(
            controls=[
                ft.Text(f"Sección: {key_clickeado}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
            ]
        )

        page.update()

    encabezado = ft.Row(
        controls=[
            ft.Icon(ft.Icons.MEDICATION, color=ft.Colors.BLUE_700, size=28),
            ft.Text("PHARMA", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Text("STOCK", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
        ],
        spacing=5,
    )

    menu_principal = ft.Column(
        controls=[
            nav_item(ft.Icons.HOME, "General", key="general", activo=True),
            nav_item(ft.Icons.INVENTORY_2, "Inventario", key="inventario"),
            nav_item(ft.Icons.PEOPLE, "Empleados", key="empleados"),
            nav_item(ft.Icons.DESCRIPTION, "Reportes", key="reportes"),
            nav_item(ft.Icons.LOCAL_SHIPPING, "Proveedores", key="proveedores"),
        ],
        spacing=8,
    )

    menu_lateral = ft.Container(
        width=240,
        bgcolor=ft.Colors.WHITE,
        padding=20,
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                menu_principal,
                ft.Container(expand=True),
                ft.Divider(color=ft.Colors.BLUE_GREY_100),
                nav_item(ft.Icons.SETTINGS, "Ajustes", key="ajustes"),
            ],
            expand=True,
        ),
    )

    contenido = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Sección: General", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
            ]
        ),
        padding=30,
        expand=True,
    )

    layout = ft.Row(
        controls=[menu_lateral, contenido],
        expand=True,
        spacing=0,
    )

    page.add(layout)