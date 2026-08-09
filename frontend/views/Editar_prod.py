import flet as ft
import flet.canvas as cv

def main(page: ft.Page):
    page.title = "Editar producto"
    page.window_width = 460
    page.window_height = 850
    page.padding = 20
    page.bgcolor = "#F4F7FB"  
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    PRIMARY_COLOR = "#5086EC"
    LIGHT_BG = "#EDF5FC"
    BORDER_COLOR = "#D1E5FB"
    TEXT_COLOR = "#1A365D"    
    
    def custom_textfield(placeholder="", value=""):
        return ft.TextField(
            value=value,
            hint_text=placeholder,
            hint_style=ft.TextStyle(color="#A0AEC0"),
            content_padding=ft.Padding.symmetric(horizontal=15, vertical=12),
            border_color=BORDER_COLOR,
            bgcolor=LIGHT_BG,
            border_radius=12,
            text_style=ft.TextStyle(color=TEXT_COLOR, weight=ft.FontWeight.W_500),
            dense=True,
        )

    def custom_dropdown(options, value=None):
        return ft.Dropdown(
            value=value if value else options[0],
            options=[ft.dropdown.Option(opt) for opt in options],
            content_padding=ft.Padding.symmetric(horizontal=15, vertical=0),
            border_color=BORDER_COLOR,
            bgcolor=LIGHT_BG,
            border_radius=12,
            text_style=ft.TextStyle(color=TEXT_COLOR, weight=ft.FontWeight.W_500),
            dense=True,
        )

    def label_text(text):
        return ft.Text(text, weight=ft.FontWeight.BOLD, color=TEXT_COLOR, size=13)

    header = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                            icon_size=16,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: print("Volver"),
                        ),
                        bgcolor="#7B93C0",
                        border_radius=20,
                        width=38,
                        height=38,
                    ),
                    ft.Text(
                        "Editar producto",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR,
                        text_align=ft.TextAlign.CENTER,
                        expand=True,
                    ),
                    ft.Container(width=38),  # Espaciador para centrar el título
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(
                controls=[
                    ft.Text(
                        "Ingresa los datos:",
                        color="#718096",
                        size=13,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                        expand=True,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=5,
    )

    #cajita de imagen 
    image_box = ft.Stack(
        controls=[
            ft.Container(
                width=135,
                height=150,
                border=ft.Border.all(1.5, BORDER_COLOR),
                content=cv.Canvas(
                    shapes=[
                        cv.Line(0, 0, 135, 150, paint=ft.Paint(color=BORDER_COLOR, stroke_width=1.5)),
                        cv.Line(0, 150, 135, 0, paint=ft.Paint(color=BORDER_COLOR, stroke_width=1.5)),
                    ],
                    width=135,
                    height=150,
                ),
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color=PRIMARY_COLOR, size=20),
                bgcolor=ft.Colors.WHITE,
                border_radius=20,
                width=36,
                height=36,
                right=0,
                bottom=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
        ]
    )

    
    right_fields = ft.Column(
        controls=[
            ft.Column([label_text("Nombre"), custom_textfield("Nombre de producto")], spacing=3),
            ft.Column([label_text("Fracción de producto"), custom_dropdown(["Fracción primera", "Fracción segunda"])], spacing=3),
            ft.Column([label_text("Tipo de medicamento"), custom_dropdown(["Analgésico", "Antibiótico"])], spacing=3),
        ],
        spacing=8,
        expand=True,
    )

    top_section = ft.Row(
        controls=[image_box, right_fields],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=15,
    )

    #Campos del cuerpo principal
    field_marca = ft.Column(
        [label_text("Marca de producto"), custom_dropdown(["Genérico", "Comercial"])],
        spacing=3,
    )

    field_caducidad = ft.Column(
        [label_text("Fecha de caducidad"), custom_textfield("01 / 12 / 2026")],
        spacing=3,
    )

    # Componente incremental (- / +) para Precio y Existencias
    def stepper_control(label, default_value):
        text_field = custom_textfield(value=default_value)
        text_field.text_align = ft.TextAlign.CENTER
        text_field.expand = True

        return ft.Column(
            controls=[
                label_text(label),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.REMOVE, color="#A0AEC0", size=18),
                            border_radius=15,
                            padding=5,
                        ),
                        text_field,
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD, color=PRIMARY_COLOR, size=18),
                            border_radius=15,
                            padding=5,
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=3,
            expand=True,
        )

    row_precio_existencias = ft.Row(
        controls=[
            stepper_control("Precio", "$ 150"),
            stepper_control("Existencias", "100 pz"),
        ],
        spacing=10,
    )

    row_lote_codigo = ft.Row(
        controls=[
            ft.Column([label_text("Lote"), custom_textfield("# 4505050")], spacing=3, expand=True),
            ft.Column([label_text("Código de barras"), custom_textfield("7 896 587 54 54")], spacing=3, expand=True),
        ],
        spacing=10,
    )

   
    divider = ft.Container(
        content=ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
        margin=ft.Margin.symmetric(vertical=10),
    )

    # Botón principal inferior
    btn_add = ft.ElevatedButton(
        content=ft.Text("Editar producto", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        style=ft.ButtonStyle(
            bgcolor=PRIMARY_COLOR,
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding.symmetric(vertical=15),
        ),
        width=float("inf"),
    )

    card_container = ft.Container(
        width=420,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 4),  
        ),
        content=ft.Column(
            controls=[
                header,
                ft.Container(height=10),
                top_section,
                field_marca,
                field_caducidad,
                row_precio_existencias,
                row_lote_codigo,
                divider,
                btn_add,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
    )  

    page.add(card_container)
ft.app(target=main)

