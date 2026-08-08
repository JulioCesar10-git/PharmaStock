import calendar
from datetime import datetime

import flet as ft

from theme import colores

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

def crear_tarjeta_calendario(page: ft.Page, fecha_activa: dict, abrir_modal_recordatorio):
    c = colores()

    fecha_actual = datetime.now()
    estado_fecha = {
        "año": fecha_actual.year,
        "mes": fecha_actual.month,
        "dia_seleccionado": fecha_actual.day,
    }

    # --- Etiqueta de mes y contenedor del grid de días ---
    lbl_mes = ft.Text(MESES_ES[estado_fecha["mes"] - 1], weight=ft.FontWeight.BOLD, color=c["input_bg"])
    grid_container = ft.Column(key="grid_calendario_clean", spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # --- Envoltura animable: desliza el grid de días al cambiar de mes ---
    grid_wrapper = ft.Container(
        content=grid_container,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        offset=ft.Offset(0, 0),
        animate_offset=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
    )

    # --- Anima la entrada del grid desde la izquierda/derecha ---
    def deslizar_mes(direccion):
        grid_wrapper.animate_offset = None
        grid_wrapper.offset = ft.Offset(direccion, 0)
        grid_wrapper.update()

        renderizar_matriz_dias()
        grid_wrapper.animate_offset = ft.Animation(280, ft.AnimationCurve.EASE_OUT)
        grid_wrapper.offset = ft.Offset(0, 0)
        grid_wrapper.update()

    # --- Marca el día elegido y abre el modal de recordatorio ---
    def seleccionar_dia(e, dia):
        estado_fecha["dia_seleccionado"] = dia
        fecha_activa["dia"] = dia
        fecha_activa["mes"] = estado_fecha["mes"]
        fecha_activa["año"] = estado_fecha["año"]
        renderizar_matriz_dias()
        abrir_modal_recordatorio(e)

    # --- Construye el grid de días del mes actual (encabezado + semanas) ---
    def renderizar_matriz_dias():
        grid_container.controls.clear()
        dias_semana = ["Dom", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]
        hdr_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(d, size=10, weight=ft.FontWeight.BOLD, color=c["texto_secundario"], text_align=ft.TextAlign.CENTER),
                    width=28,
                    alignment=ft.Alignment.CENTER,
                )
                for d in dias_semana
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )
        grid_container.controls.append(hdr_row)
        cal = calendar.Calendar(firstweekday=6)
        dias_mes = cal.monthdayscalendar(estado_fecha["año"], estado_fecha["mes"])

        # --- Días (de cualquier mes/año) que tienen tareas o recordatorios pendientes ---
        obtener_dias_con_tareas = fecha_activa.get("_obtener_dias_con_tareas")
        dias_con_tareas = obtener_dias_con_tareas() if obtener_dias_con_tareas else set()

        for semana in dias_mes:
            fila_controles = []
            for dia in semana:
                if dia == 0:
                    fila_controles.append(ft.Container(width=28, height=28))
                else:
                    es_seleccionado = dia == estado_fecha["dia_seleccionado"]
                    tiene_tarea = (dia, estado_fecha["mes"], estado_fecha["año"]) in dias_con_tareas

                    btn_dia = ft.Container(
                        content=ft.Text(
                            str(dia),
                            size=11,
                            weight=ft.FontWeight.BOLD if es_seleccionado else ft.FontWeight.NORMAL,
                            color=ft.Colors.WHITE if es_seleccionado else c["input_bg"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=28,
                        height=28,
                        border_radius=14,
                        bgcolor=c["azul_card"] if es_seleccionado else None,
                        alignment=ft.Alignment.CENTER,
                        ink=True,
                        on_click=lambda e, d=dia: seleccionar_dia(e, d),
                    )

                    if tiene_tarea:
                        # Burbuja pequeña de "tiene tarea", en color distinto al de
                        # selección (azul_card), para no confundirse con el día activo.
                        punto_tarea = ft.Container(
                            width=6,
                            height=6,
                            border_radius=3,
                            bgcolor=ft.Colors.ORANGE_600,
                            top=21,
                            left=11,
                        )
                        celda_dia = ft.Stack(controls=[btn_dia, punto_tarea], width=28, height=28)
                    else:
                        celda_dia = btn_dia

                    fila_controles.append(celda_dia)

            grid_container.controls.append(
                ft.Row(controls=fila_controles, alignment=ft.MainAxisAlignment.CENTER, spacing=4)
            )

    # --- Selector de año ---
    def cambiar_anio(e):
        if dd_anio.value:
            estado_fecha["año"] = int(dd_anio.value)
            renderizar_matriz_dias()
            page.update()

    anios_disponibles = [str(y) for y in range(fecha_actual.year - 10, fecha_actual.year + 11)]

    dd_anio = ft.Dropdown(
        value=str(estado_fecha["año"]),
        options=[ft.dropdown.Option(a) for a in anios_disponibles],
        width=95,
        height=35,
        text_size=12,
        border_color=c["azul_card"],
        border_radius=8,
        content_padding=ft.Padding.symmetric(horizontal=8, vertical=0),
        color=c["input_bg"],
        text_style=ft.TextStyle(color=c["input_bg"], weight=ft.FontWeight.BOLD),
        trailing_icon=ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=c["input_bg"]),
        on_select=cambiar_anio,
    )

    # --- Navegación entre meses ---
    def mes_anterior(e):
        if estado_fecha["mes"] == 1:
            estado_fecha["mes"] = 12
            estado_fecha["año"] -= 1
        else:
            estado_fecha["mes"] -= 1

        lbl_mes.value = MESES_ES[estado_fecha["mes"] - 1]
        dd_anio.value = str(estado_fecha["año"])
        deslizar_mes(-1)
        page.update()

    def mes_siguiente(e):
        if estado_fecha["mes"] == 12:
            estado_fecha["mes"] = 1
            estado_fecha["año"] += 1
        else:
            estado_fecha["mes"] += 1

        lbl_mes.value = MESES_ES[estado_fecha["mes"] - 1]
        dd_anio.value = str(estado_fecha["año"])
        deslizar_mes(1)
        page.update()

    # --- Regresa la selección (y la vista) a la fecha actual del sistema ---
    def resetear_a_hoy():
        hoy = datetime.now()
        estado_fecha["año"] = hoy.year
        estado_fecha["mes"] = hoy.month
        estado_fecha["dia_seleccionado"] = hoy.day
        fecha_activa["dia"] = hoy.day
        fecha_activa["mes"] = hoy.month
        fecha_activa["año"] = hoy.year

        lbl_mes.value = MESES_ES[estado_fecha["mes"] - 1]
        dd_anio.value = str(estado_fecha["año"])
        renderizar_matriz_dias()

    # --- Vuelve a dibujar el grid sin mover la selección ni el mes/año en vista ---
    # Útil para cuando una tarea se agrega o se completa desde otra parte de la app.
    def actualizar_marcadores():
        renderizar_matriz_dias()

    # Se registran en fecha_activa para que otros módulos (recordatorios)
    # puedan invocarlas sin necesidad de importarse entre sí.
    fecha_activa["_resetear_calendario"] = resetear_a_hoy
    fecha_activa["_refrescar_calendario"] = actualizar_marcadores

    renderizar_matriz_dias()

    # --- Ensamblado final de la tarjeta de calendario ---
    return ft.Container(
        bgcolor=c["fondo_card"],
        border_radius=20,
        padding=15,
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
                        ft.Icon(ft.Icons.CALENDAR_MONTH, color=c["input_bg"], size=20),
                        ft.Text("CALENDARIO", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=14),
                    ],
                    spacing=8,
                ),
                ft.Container(
                    bgcolor=c["bg_card_white"],
                    border_radius=20,
                    padding=10,
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
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_LEFT,
                                        icon_size=18,
                                        icon_color=c["azul_card"],
                                        on_click=mes_anterior,
                                        padding=0,
                                    ),
                                    lbl_mes,
                                    ft.Container(expand=True),
                                    dd_anio,
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_RIGHT,
                                        icon_size=18,
                                        icon_color=c["azul_card"],
                                        on_click=mes_siguiente,
                                        padding=0,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=5, color="transparent"),
                            grid_wrapper,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ]
        ),
    )