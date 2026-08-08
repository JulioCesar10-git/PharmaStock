from datetime import datetime

import flet as ft

from frontend.theme import colores
from frontend.views.reportes import obtener_ganancias_por_mes, obtener_anios_disponibles, MESES_ABREV

ANCHO_BARRAS = 230  # ancho (px) disponible para la barra más larga
NIVELES_EJE = 7       # cantidad de marcas de referencia
PASO_ESCALA_FIJO = 1000  # separación fija entre marcas
ESCALA_INICIO = 8000  # valor de la primera marca: 8K, 9K, 10K, 11K, 12K, 13K, 14K


# --- Da formato corto tipo "$20K" o "$350" a un monto ---
def _formatear_dinero(valor):
    if valor >= 1000:
        texto = f"{valor / 1000:.1f}".rstrip("0").rstrip(".")
        return f"${texto}K"
    return f"${valor:.0f}"


def crear_tarjeta_ganancias():
    c = colores()
    hoy = datetime.now()

    # --- Años disponibles según los reportes existentes (más reciente primero) ---
    anios_disponibles = [int(a) for a in obtener_anios_disponibles()] or [hoy.year]
    estado = {"anio": hoy.year if hoy.year in anios_disponibles else anios_disponibles[0]}

    # --- Botón/chip para elegir un año ---
    def _crear_boton_anio(anio):
        seleccionado = anio == estado["anio"]

        def _al_hacer_click(e, a=anio):
            estado["anio"] = a
            contenedor_tarjeta.content = _construir_contenido()
            # Se usa la página del propio evento: al haberse podido hacer clic,
            # el control ya está montado y su página es válida.
            if e.page:
                e.page.update()

        return ft.Container(
            content=ft.Text(
                str(anio),
                size=12,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE if seleccionado else c["input_bg"],
            ),
            bgcolor=c["azul_card"] if seleccionado else ft.Colors.with_opacity(0.12, c["azul_card"]),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
            on_click=_al_hacer_click,
            ink=True,
        )

    # --- Construye el contenido completo de la tarjeta para el año seleccionado ---
    def _construir_contenido():
        anio = estado["anio"]

        totales_por_mes = obtener_ganancias_por_mes(anio)
        valores = [totales_por_mes.get(mes, 0.0) for mes in range(1, 13)]
        ganancia_anual = sum(valores)
        paso_escala = PASO_ESCALA_FIJO
        max_y = ESCALA_INICIO + paso_escala * (NIVELES_EJE - 1)

        # --- Escala superior de referencia (0 -> techo de la gráfica) ---
        fila_escala = ft.Row(
            [
                ft.Container(width=30),
                ft.Container(
                    width=ANCHO_BARRAS,
                    content=ft.Row(
                        [
                            ft.Text(
                                _formatear_dinero(ESCALA_INICIO + paso_escala * nivel),
                                size=11,
                                color=c["texto_secundario"],
                                no_wrap=True,
                            )
                            for nivel in range(NIVELES_EJE)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=0,
                    ),
                ),
            ],
            spacing=8,
        )

        # --- Ancho de la barra proporcional a su posición dentro del rango
        #     visible de la escala (de ESCALA_INICIO a max_y), igual que la
        #     fila de números de arriba, NO desde 0 ---
        def _ancho_barra_en_escala(valor):
            if valor <= 0:
                return 0
            if valor <= ESCALA_INICIO:
                return 3  # valor positivo pero por debajo de la primera marca
            proporcion = (valor - ESCALA_INICIO) / (max_y - ESCALA_INICIO)
            return max(3, min(ANCHO_BARRAS, proporcion * ANCHO_BARRAS))

        # --- Una fila horizontal por cada mes del año seleccionado ---
        filas_meses = []
        for i, valor in enumerate(valores):
            mes_num = i + 1
            ancho_barra = _ancho_barra_en_escala(valor)
            es_mes_actual = anio == hoy.year and mes_num == hoy.month

            filas_meses.append(
                ft.Row(
                    [
                        ft.Text(
                            MESES_ABREV[i],
                            size=12,
                            width=30,
                            color=c["input_bg"],
                            weight=ft.FontWeight.BOLD if es_mes_actual else ft.FontWeight.NORMAL,
                        ),
                        ft.Stack(
                            [
                                ft.Container(
                                    width=ANCHO_BARRAS,
                                    height=12,
                                    bgcolor=ft.Colors.with_opacity(0.12, c["azul_card"]),
                                    border_radius=6,
                                ),
                                ft.Container(
                                    width=ancho_barra,
                                    height=12,
                                    bgcolor=c["azul_card"] if es_mes_actual else c["boton_secundario"],
                                    border_radius=6,
                                    tooltip=f"{MESES_ABREV[i]} {anio}: {_formatear_dinero(valor)}",
                                ),
                            ],
                            width=ANCHO_BARRAS,
                            height=12,
                        ),
                        ft.Text(_formatear_dinero(valor), size=12, color=c["texto_secundario"]),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )

        columna_meses = ft.Column(
            filas_meses,
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.MONETIZATION_ON, color=c["input_bg"], size=20),
                        ft.Text("GANANCIAS", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=14),
                        ft.Container(expand=True),
                        ft.Row(
                            [_crear_boton_anio(a) for a in anios_disponibles],
                            spacing=6,
                        ),
                    ],
                    spacing=8,
                ),
                # --- Panel del gráfico: meses en vertical + barras horizontales ---
                ft.Container(
                    bgcolor=c["bg_card_white"],
                    border_radius=20,
                    padding=15,
                    height=270,
                    shadow=ft.BoxShadow(
                        blur_radius=10,
                        spread_radius=1,
                        color=c["sombra"],
                        offset=ft.Offset(0, 3),
                    ),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(expand=True),
                                    ft.Text(
                                        f"{_formatear_dinero(ganancia_anual)} en {anio}",
                                        size=12,
                                        color=c["texto_secundario"],
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            fila_escala,
                            columna_meses,
                        ],
                        spacing=8,
                        expand=True,
                    ),
                ),
            ],
            expand=True,
        )

    # --- Tarjeta contenedora; se reconstruye por completo al cambiar de año ---
    contenedor_tarjeta = ft.Container(
        expand=True,
        bgcolor=c["fondo_card"],
        border_radius=20,
        padding=15,
        shadow=ft.BoxShadow(
            blur_radius=10,
            spread_radius=1,
            color=c["sombra"],
            offset=ft.Offset(0, 3),
        ),
        content=None,
    )

    contenedor_tarjeta.content = _construir_contenido()

    return contenedor_tarjeta