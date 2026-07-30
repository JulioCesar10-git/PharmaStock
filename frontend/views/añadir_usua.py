import flet as ft
import flet.canvas as cv


def main(page: ft.Page):
    page.title = "Añadir usuario"
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

    def custom_textfield(
        placeholder="", value="", password=False, can_reveal_password=False
    ):
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
            password=password,
            can_reveal_password=can_reveal_password,
        )

    def custom_dropdown(options, value=None):
        return ft.Dropdown(
            value=value if value else options[0],
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

    # --- Header ---
    header = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.IconButton(
                            icon="arrow_back_ios_new",
                            icon_size=16,
                            icon_color=PRIMARY_COLOR,
                            on_click=lambda _: print("Volver"),
                        ),
                        bgcolor=LIGHT_BG,
                        border_radius=20,
                        width=38,
                        height=38,
                    ),
                    ft.Text(
                        "Añadir usuario",
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

    # --- Caja de imagen de perfil ---
    image_box = ft.Stack(
        controls=[
            ft.Container(
                width=135,
                height=150,
                border=ft.Border.all(1.5, BORDER_COLOR),
                border_radius=10,
                content=cv.Canvas(
                    shapes=[
                        cv.Line(
                            0,
                            0,
                            135,
                            150,
                            paint=ft.Paint(
                                color=BORDER_COLOR, stroke_width=1.5
                            ),
                        ),
                        cv.Line(
                            0,
                            150,
                            135,
                            0,
                            paint=ft.Paint(
                                color=BORDER_COLOR, stroke_width=1.5
                            ),
                        ),
                    ],
                    width=135,
                    height=150,
                ),
            ),
            ft.Container(
                content=ft.Icon(
                    "image_outlined", color=PRIMARY_COLOR, size=20
                ),
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

    # --- Sección Superior Derecha ---
    right_fields = ft.Column(
        controls=[
            ft.Column(
                [
                    label_text("Apellidos"),
                    custom_textfield("Ingresa apellidos"),
                ],
                spacing=3,
            ),
            ft.Column(
                [label_text("Nombre"), custom_textfield("Ingresa nombre")],
                spacing=3,
            ),
            ft.Column(
                [
                    label_text("Puesto"),
                    custom_dropdown(["Cajero", "Bodeguero"]),
                ],
                spacing=3,
            ),
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

    # --- Sección de Teléfono (LADA + Número) ---
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

    # --- Crear Contraseña ---
    field_password = ft.Column(
        controls=[
            label_text("Crear contraseña"),
            custom_textfield(
                placeholder="Ingresa +8 caracteres",
                password=True,
                can_reveal_password=True,
            ),
        ],
        spacing=3,
    )

    divider = ft.Container(
        content=ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
        margin=ft.Margin.symmetric(vertical=10),
    )

    # --- Botón Principal ---
    btn_add = ft.ElevatedButton(
        content=ft.Text(
            "Añadir usuario",
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

    # --- Tarjeta Contenedora Principal ---
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
                field_telefono,
                field_correo,
                field_password,
                divider,
                btn_add,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.add(card_container)


ft.app(target=main)