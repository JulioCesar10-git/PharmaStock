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