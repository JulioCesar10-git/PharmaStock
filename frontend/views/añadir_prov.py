import flet as ft


def main(page: ft.Page):
    page.title = "Añadir proveedor"
    page.window_width = 460
    page.window_height = 850
    page.padding = 20
    page.bgcolor = "#F4F7FB"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    PRIMARY_COLOR = "#879BC2"  
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
            text_style=ft.TextStyle(
                color=TEXT_COLOR, weight=ft.FontWeight.W_500
            ),
            dense=True,
        )

    def custom_dropdown(options, value=None, hint_text=""):
        return ft.Dropdown(
            value=value if value else (options[0] if options else None),
            hint_text=hint_text,
            options=[ft.dropdown.Option(opt) for opt in options],
            content_padding=ft.Padding.symmetric(horizontal=15, vertical=0),
            border_color=BORDER_COLOR,
            bgcolor=LIGHT_BG,
            border_radius=12,
            text_style=ft.TextStyle(
                color=TEXT_COLOR, weight=ft.FontWeight.W_500
            ),
            dense=True,
        )

    def label_text(text):
        return ft.Text(
            text, weight=ft.FontWeight.BOLD, color=TEXT_COLOR, size=13
        )

    #  Header 
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
                        "Añadir proveedor",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR,
                        text_align=ft.TextAlign.CENTER,
                        expand=True,
                    ),
                    ft.Container(width=38),  # Espaciador para centrar
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

    # Nombre
    field_nombre = ft.Column(
        controls=[
            label_text("Nombre"),
            custom_textfield("Nombre de proveedor"),
        ],
        spacing=3,
    )

    # Telefono
    field_telefono = ft.Column(
        controls=[
            label_text("Número telefónico"),
            ft.Row(
                controls=[
                    ft.Container(
                        content=custom_dropdown(
                            ["+52", "+1", "+34"], value="+52"
                        ),
                        width=90,
                    ),
                    ft.Container(
                        content=custom_textfield("241 569 5694"), expand=True
                    ),
                ],
                spacing=10,
            ),
        ],
        spacing=3,
    )

    # --- Correo Electrónico ---
    field_correo = ft.Column(
        controls=[
            label_text("Correo electrónico"),
            custom_textfield("ejemplo@gmail.com"),
        ],
        spacing=3,
    )

    # --- Divisor Dirección ---
    divider_direccion = ft.Row(
        controls=[
            ft.Container(
                content=ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                expand=True,
            ),
            ft.Text(
                "Dirección",
                color=TEXT_COLOR,
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
            ft.Container(
                content=ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                expand=True,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # --- Código Postal ---
    field_cp = ft.Column(
        controls=[
            label_text("Código postal"),
            custom_textfield("90 100"),
        ],
        spacing=3,
    )

    # --- Número y Calle ---
    field_numero_calle = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    label_text("Número"),
                    ft.Container(
                        content=custom_dropdown(
                            ["30", "31", "32"], value="30"
                        ),
                        width=100,
                    ),
                ],
                spacing=3,
            ),
            ft.Column(
                controls=[
                    label_text("Calle"),
                    custom_dropdown(
                        ["Av. Juárez", "Calle Hidalgo", "Calle 5 de Mayo"],
                        hint_text="Seleccionar calle",
                    ),
                ],
                spacing=3,
                expand=True,
            ),
        ],
        spacing=10,
    )

    # --- Divisor inferior ---
    divider_bottom = ft.Container(
        content=ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
        margin=ft.Margin.symmetric(vertical=5),
    )

    # --- Botón Principal ---
    btn_add = ft.ElevatedButton(
        content=ft.Text(
            "Añadir proveedor",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
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
                field_nombre,
                field_telefono,
                field_correo,
                divider_direccion,
                field_cp,
                field_numero_calle,
                divider_bottom,
                btn_add,
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.add(card_container)


ft.app(target=main)