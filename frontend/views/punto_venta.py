import flet as ft

#paleta de colores
PRIMARY_COLOR = "#5086EC"
LIGHT_BG = "#EDF5FC"
BORDER_COLOR = "#D1E5FB"
TEXT_COLOR = "#1A365D"  


def border_all(width, color):
    side = ft.BorderSide(width=width, color=color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def main(page: ft.Page):
    page.title = "Punto de venta"
    page.bgcolor = "white"
    page.padding = 10
    page.window.width = 1366
    page.window.height = 768
    page.fonts = {"Quicksand": "https://raw.githubusercontent.com/google/fonts/main/ofl/quicksand/Quicksand[wght].ttf"}
    page.theme = ft.Theme(
    font_family="Quicksand",
    text_theme=ft.TextTheme(
        body_large=ft.TextStyle(weight=ft.FontWeight.W_600, color= "black"),
        body_medium=ft.TextStyle(weight=ft.FontWeight.W_600, color = "black"),
        body_small=ft.TextStyle(weight=ft.FontWeight.W_600, color = "black"),
        label_large=ft.TextStyle(weight=ft.FontWeight.W_600, color = "black"),
    ),
)

    # ---------------------------------------------------------------
    # PANEL IZQUIERDO: TICKET
    # ---------------------------------------------------------------

    ticket_header = ft.Container(
        content=ft.Text("TICKET       FOLIO: 23384",
                         color="black", size=14, weight=ft.FontWeight.BOLD),
        bgcolor= "#EDF5FC",
        padding=ft.Padding(left=10, top=6, right=10, bottom=6),
        border_radius=14,
    )

    def linea_producto(nombre, precio, pieza, pieza_precio):
        return ft.Column(
            [
                ft.Row(
                    [ft.Text(nombre, size=17), ft.Text(precio, size=17)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [ft.Text(pieza, size=17), ft.Text(precio_calc := pieza_precio, size=17)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=0,
        )

    ticket_body = ft.Container(
        bgcolor="#EDF5FC",
        padding=20,
        expand=True,
        border_radius=14,
        content=ft.Column(
            [
                ft.Text("Fecha y hora: 16/03/2026 10:15:15", size=20, color="black"),
                ft.Container(height=15),
                linea_producto("   4 DEXTORMETORFANO", "224.00", "600MG", "56.00"),
                linea_producto("   2 ACICLOVIR COMPUESTO", "212.00", "250MG", "53.00"),
                linea_producto("   6 JERINGAS 5ML", "162.00", "PIEZA 2", "27.00"),
                ft.Container(height=10),
                ft.Text("# Artículos : 20.000", size=18, color="black"),
                ft.Container(height=10),
                ft.Row([ft.Container(width=60), ft.Text("Total    :", size=20, color="black"),
                        ft.Text("$817.00", size=20, color="black")], spacing=10),
                ft.Row([ft.Container(width=60), ft.Text("Recibido :", size=20, color="black"),
                        ft.Text("$817.00", size=20, color="black")], spacing=10),
                ft.Row([ft.Container(width=60), ft.Text("Efectivo :", size=20, color="black"),
                        ft.Text("$817.00", size=20, color="black")], spacing=10),
                ft.Row([ft.Container(width=60), ft.Text("Su Cambio:", size=20, color="black"),
                        ft.Text("$0.00", size=20, color="black")], spacing=10),
                ft.Container(height=10),
                ft.Text("OCHOCIENTOS DIECISIETE  PESOS 00/100 MN", size=20, color="black"),
                ft.Container(height=25),
                ft.Row([ft.Container(expand=True), ft.Text("FACTURAS WHASTAPP", size=20, color="black")]),
            ],
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    ticket_panel = ft.Container(
        content=ft.Column([ticket_header, ticket_body], spacing=0, expand=True),
        expand=1,
    )

    # ---------------------------------------------------------------
    # PANEL DERECHO: POS
    # ---------------------------------------------------------------

    top_bar = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Row(
            [
                ft.Text("10:49 a. m.", color="#0B2B63", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("lunes , 16 de marzo de 2026", size=14, color="black"),
                ft.Container(expand=True),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    total_box = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Column(
            [
                ft.Text("Artículos 20", size=22, color="black"),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Subtotal $704.31", size=13, color="grey"),
                                ft.Text("Impuesto $112.69", size=13, color="grey"),
                                ft.Text("Total $817.00", size=26, color="#1565c0", weight=ft.FontWeight.BOLD),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),

                        ft.Column(
                            [
                                ft.Text("PHARMA STOCK", size=20, color="#1A365D", weight=ft.FontWeight.BOLD),
                                ft.Text("F A R M A C I A", size=9, color="grey"),
                            ],
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        ),
                    ],
                ),
            ],
        ),
    )

    pregunta_box = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    bgcolor="#EDF5FC",
                    padding=10,
                    border_radius =14,
                    content=ft.Column(
                        [
                            ft.Text("¿Se borra lista?", size=14, color="black"),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "Si", bgcolor ="#4F7FE0"  , color="white", expand=True,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                                    ),
                                    ft.ElevatedButton(
                                        "No", bgcolor="white", color="black", expand=True,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                    ),
                ),
            ],
            spacing=0,
        ),
        border_radius = 14,
    )

    usuario_codbarr_row = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius = 14,
        content=ft.Row(
            [
                ft.Text("Codigo barras", size=12, color="grey"),
                ft.Container(expand=True),
                ft.Container(
                    width = 210,
                    height=40,
                    border=border_all(2, "#5086EC"),
                    bgcolor="white",
                    border_radius=14,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON_OUTLINE, color="#5086EC"),
                    bgcolor="#f5f5f5",
                    padding=8,
                    border=border_all(1, "#cccccc"),
                    border_radius = 14,
                ),
                ft.Container(
                    width = 180,
                    height=40,
                    border=border_all(2, "#5086EC"),
                    bgcolor="white",
                    border_radius=14
                ),
                ft.Container(expand = True )
            ],
            spacing=10,
        ),
    )

    def funcion_btn(texto, sub, bgcolor="#EDF5FC", color="black", expand=1, border_radius = 14,):
        return ft.Container(
            content=ft.Column(
                [ft.Text(texto, size=13, color=color), ft.Text(sub, size=11, color=color)]
                if sub else [ft.Text(texto, size=13, color=color)],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=bgcolor,
            border=border_all(1, "#cccccc"),
            padding=10,
            expand=expand,
            alignment=ft.Alignment(0, 0),
            height=55,
            border_radius = border_radius,
        )

    botones_grid = ft.Column(
        [
            ft.Row(
                [
                    funcion_btn("+ Agregar", None),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    funcion_btn("Cantidad", None),
                    ft.Container(
                        content=ft.Text("1", size=16, color="#1565c0"),
                        alignment=ft.Alignment(0, 0), expand=1,
                    ),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    funcion_btn("Monto recibido", None, expand=4, color="#A9C2E8" ),
                    funcion_btn("Cobrar", None, bgcolor="#4F7FE0", color="white"),
                ],
                spacing=6,
            ),
        ],
        spacing=6,
    )

    otros_botones = ft.Column(
        [
            ft.Row([funcion_btn("Nuevo", None, expand=1), funcion_btn("Regresar", None, expand=1)],spacing=6,),
        ],
        spacing=6,
    )

    def numpad_btn(texto):
        return ft.Container(
            content=ft.Text(texto, size=18, color="black"),
            bgcolor="#EDF5FC",
            border=border_all(1, "#cccccc"),
            alignment=ft.Alignment(0, 0),
            width=55,
            height=55,
        )

    numpad = ft.Column(
        [
            ft.Row([numpad_btn("1"), numpad_btn("2"), numpad_btn("3")], spacing=6),
            ft.Row([numpad_btn("4"), numpad_btn("5"), numpad_btn("6")], spacing=6),
            ft.Row([numpad_btn("7"), numpad_btn("8"), numpad_btn("9")], spacing=6),
            ft.Row([numpad_btn("."), numpad_btn("0"), numpad_btn("⌫")], spacing=6),
        ],
        spacing=6,
    )

    right_panel = ft.Container(
        content=ft.Column(
            [
                top_bar,    
                total_box,
                pregunta_box,
                usuario_codbarr_row,
                ft.Row(
                    [
                        ft.Container(content=botones_grid, expand=2),
                        ft.Container(content=numpad, expand=1),
                    ],
                    spacing=10,
                ),
                otros_botones,
            ],
            spacing=10,
        ),
        expand=1,
        bgcolor= "white",
        padding=10,
    )

    # ---------------------------------------------------------------
    # LAYOUT GENERAL
    # ---------------------------------------------------------------
    page.add(
        ft.Row(
            [ticket_panel, right_panel],
            expand=True,
            spacing=10,
        )
    )
if __name__ == "__main__":
    ft.run(main)





