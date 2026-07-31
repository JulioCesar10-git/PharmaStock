import flet as ft

def main(page: ft.Page):
    page.title = "Añadir reporte de CPM - PharmaStock"
    page.bgcolor = "#DDE7F5"  # Fondo de la pantalla principal
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Estilos de Colores ---
    NAVY_TITLE = "#0F2851"
    SUBTITLE_TEXT = "#4A6B94"
    BLUE_BORDER = "#B4D0FB"
    BLUE_INPUT_BG = "#E8F1FD"
    BLUE_DISABLED_BG = "#9BBDF3"
    BUTTON_BG = "#5086EC"

    
    def dashed_section_header(title: str):
        return ft.Row(
            controls=[
                ft.Text("-----------------", color=BLUE_BORDER, size=12, weight=ft.FontWeight.BOLD),
                ft.Text(title, color=NAVY_TITLE, size=14, weight=ft.FontWeight.BOLD),
                ft.Text("-----------------", color=BLUE_BORDER, size=12, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

     
    day_dropdown = ft.Dropdown(
        value="01",
        options=[ft.dropdown.Option(f"{i:02d}") for i in range(1, 32)],
        border_radius=15,
        border_color=BLUE_BORDER,
        bgcolor=BLUE_INPUT_BG,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=0),
        dense=True,
        expand=True,
    )

    month_dropdown = ft.Dropdown(
        value="Julio",
        options=[
            ft.dropdown.Option("Enero"), ft.dropdown.Option("Febrero"),
            ft.dropdown.Option("Marzo"), ft.dropdown.Option("Abril"),
            ft.dropdown.Option("Mayo"), ft.dropdown.Option("Junio"),
            ft.dropdown.Option("Julio"), ft.dropdown.Option("Agosto"),
            ft.dropdown.Option("Septiembre"), ft.dropdown.Option("Octubre"),
            ft.dropdown.Option("Noviembre"), ft.dropdown.Option("Diciembre")
        ],
        border_radius=15,
        border_color=BLUE_BORDER,
        bgcolor=BLUE_INPUT_BG,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=0),
        dense=True,
        expand=True,
    )

    year_dropdown = ft.Dropdown(
        value="2026",
        options=[ft.dropdown.Option(str(y)) for y in range(2020, 2031)],
        border_radius=15,
        border_color=BLUE_BORDER,
        bgcolor=BLUE_INPUT_BG,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=0),
        dense=True,
        expand=True,
    )

    row_inicio = ft.Row(
        controls=[
            ft.Column([ft.Text("Día", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), day_dropdown], expand=1),
            ft.Column([ft.Text("Mes", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), month_dropdown], expand=1),
            ft.Column([ft.Text("Año", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), year_dropdown], expand=1),
        ],
        spacing=10,
    )


    def read_only_box(text_value: str):
        return ft.Container(
            content=ft.Text(text_value, color=NAVY_TITLE, weight=ft.FontWeight.W_500, size=14),
            bgcolor=BLUE_DISABLED_BG,
            border_radius=15,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            alignment=ft.Alignment(-1,0),
            expand=True,
        )

    row_final = ft.Row(
        controls=[
            ft.Column([ft.Text("Día", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), read_only_box("31")], expand=1),
            ft.Column([ft.Text("Mes", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), read_only_box("Julio")], expand=1),
            ft.Column([ft.Text("Año", color=NAVY_TITLE, weight=ft.FontWeight.BOLD, size=13), read_only_box("2026")], expand=1),
        ],
        spacing=10,
    )

    
    modal_card = ft.Container(
        width=480,
        bgcolor=ft.Colors.WHITE,
        border_radius=25,
        padding=25,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.BLACK_12,
            offset=ft.Offset(0, 4)
        ),
        content=ft.Column(
            controls=[
                # Encabezado con Botón Regresar y Título
                ft.Stack(
                    controls=[
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_ROUNDED,
                                icon_color=ft.Colors.WHITE,
                                icon_size=20,
                                on_click=lambda e: print("Regresar clicado"),
                            ),
                            bgcolor="#7B93C0",
                            shape=ft.BoxShape.CIRCLE,
                            width=40,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Añadir reporte de CPM", color=NAVY_TITLE, size=20, weight=ft.FontWeight.BOLD),
                                ft.Text("Consumo promedio mensual", color=SUBTITLE_TEXT, size=13),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            width=430,
                        ),
                    ]
                ),
                
                ft.Container(height=10),

                # Sección Rango Inicio
                dashed_section_header("Rango de fecha (inicio)"),
                ft.Container(height=5),
                row_inicio,

                ft.Container(height=10),

                # Sección Rango Final
                dashed_section_header("Rango de fecha (final)"),
                ft.Container(height=5),
                row_final,

                ft.Container(height=10),

                # Texto informativo central
                ft.Text(
                    "Se colocará automáticamente el final del rango de fecha\ndel reporte tomando en cuenta el inicio del mismo",
                    color=SUBTITLE_TEXT,
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=5),

                
                ft.Text("-------------------------------------------------------------------------", color=BLUE_BORDER, size=11),

                ft.Container(height=5),

                # Boton "Añadir reporte"
                ft.ElevatedButton(
                    content=ft.Text("Añadir reporte", color=ft.Colors.WHITE, size=15, weight=ft.FontWeight.W_500),
                    style=ft.ButtonStyle(
                        bgcolor=BUTTON_BG,
                        shape=ft.RoundedRectangleBorder(radius=20),
                        elevation=2,
                    ),
                    width=430,
                    height=45,
                    on_click=lambda e: print("Reporte añadido"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
    )

    page.add(modal_card)

ft.app(target=main)