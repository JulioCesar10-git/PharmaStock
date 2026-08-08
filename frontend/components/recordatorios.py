import flet as ft

from theme import colores

# --- Aplica el mismo efecto hover del botón "Agregar tarea"
#     (zoom + sombra más marcada, sin marco) a un Container-botón ---
def _aplicar_hover_boton(boton, sombra_normal, sombra_hover, escala_hover=1.06):
    def _resolver(s):
        return s() if callable(s) else s

    boton.scale = 1.0
    boton.shadow = _resolver(sombra_normal)
    boton.animate_scale = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)
    boton.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)

    def _al_pasar_mouse(e):
        esta_hover = str(e.data).lower() in ["true", "1"]
        if esta_hover:
            boton.scale = escala_hover
            boton.shadow = _resolver(sombra_hover)
        else:
            boton.scale = 1.0
            boton.shadow = _resolver(sombra_normal)
        boton.update()

    boton.on_hover = _al_pasar_mouse

def crear_modulo_recordatorios(page: ft.Page, fecha_activa: dict):
    lista_tareas_data = []
    columna_tareas_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    # --- Lista de avisos (usada por la campanita de notificaciones) ---
    lista_avisos_data = []

    def obtener_lista():
        return lista_avisos_data

    def agregar_aviso(texto):
        lista_avisos_data.insert(0, texto)

    # --- Devuelve el conjunto de días (dia, mes, año) con tareas pendientes ---
    # Se registra en fecha_activa para que calendario.py pueda leerlo sin
    # necesidad de importar este módulo (evita dependencias circulares).
    def obtener_dias_con_tareas():
        dias = set()
        for t in lista_tareas_data:
            try:
                dia_str, mes_str, año_str = t["fecha"].split("/")
                dias.add((int(dia_str), int(mes_str), int(año_str)))
            except (ValueError, KeyError):
                continue
        return dias

    fecha_activa["_obtener_dias_con_tareas"] = obtener_dias_con_tareas

    # --- Dibuja/redibuja la lista de tarjetas de tareas ---
    def renderizar_tareas():
        c = colores()

        # --- Diálogo de confirmación al marcar una tarea como completada ---
        def confirmar_eliminacion(e, tarea):
            def borrar_y_cerrar(e):
                lista_tareas_data.remove(tarea)
                modal_confirmacion.open = False
                renderizar_tareas()

                # Al completar la tarea, se borra su burbuja del calendario
                refrescar_calendario = fecha_activa.get("_refrescar_calendario")
                if refrescar_calendario:
                    refrescar_calendario()

                page.update()

            # --- Botones del diálogo, con el mismo efecto hover (zoom + sombra) ---
            SOMBRA_NORMAL_DLG = ft.BoxShadow(blur_radius=8, spread_radius=1, color=c.get("sombra", "#A9B8CE"), offset=ft.Offset(0, 2))
            SOMBRA_HOVER_DLG = ft.BoxShadow(blur_radius=12, spread_radius=2, color=c.get("sombra", "#A9B8CE"), offset=ft.Offset(0, 3))

            btn_cancelar = ft.Container(
                content=ft.Text("Cancelar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                border_radius=16,
                bgcolor=c["boton_secundario"],
                shadow=SOMBRA_NORMAL_DLG,
                on_click=lambda e: setattr(modal_confirmacion, "open", False) or page.update(),
                ink=True,
            )
            _aplicar_hover_boton(btn_cancelar, SOMBRA_NORMAL_DLG, SOMBRA_HOVER_DLG, escala_hover=1.05)

            btn_aceptar = ft.Container(
                content=ft.Text("Aceptar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                border_radius=16,
                bgcolor=c["text_red"],
                on_click=borrar_y_cerrar,
                ink=True,
            )
            _aplicar_hover_boton(btn_aceptar, SOMBRA_NORMAL_DLG, SOMBRA_HOVER_DLG, escala_hover=1.05)

            # --- AlertDialog de confirmación ---
            modal_confirmacion = ft.AlertDialog(
                title=ft.Text("Confirmar eliminación", color=c["input_bg"], weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"¿Estás seguro de que deseas marcar como completada y eliminar la tarea:\n\"{tarea['titulo']}\"?",
                    color=c["input_bg"],
                ),
                actions=[btn_cancelar, btn_aceptar],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.overlay.append(modal_confirmacion)
            modal_confirmacion.open = True
            page.update()

        # --- Reconstruye las tarjetas de cada tarea ---
        columna_tareas_list.controls.clear()

        if not lista_tareas_data:
            columna_tareas_list.controls.append(
                ft.Text("No hay recordatorios pendientes", color=c["input_bg"], italic=True)
            )
        else:
            for t in lista_tareas_data:
                columna_tareas_list.controls.append(
                    ft.Container(
                        bgcolor=c["bg_card_white"],
                        border_radius=10,
                        padding=12,
                        shadow=ft.BoxShadow(
                                blur_radius=10,
                                spread_radius=1,
                                color=c.get("sombra", "#A9B8CE"),
                                offset=ft.Offset(0, 3),
                            ),
                        content=ft.Column(
                            [
                                ft.Text(t["titulo"], weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                                ft.Row(
                                    [
                                        ft.Text(t["fecha"], size=12, color=c["input_bg"], weight=ft.FontWeight.BOLD),
                                        ft.ElevatedButton(
                                            "Completada",
                                            icon=ft.Icons.CHECK_CIRCLE,
                                            bgcolor=c["bg_card_white"],
                                            color=c["input_bg"],
                                            icon_color=c["input_bg"],
                                            elevation=0,
                                            height=32,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=8),
                                                padding=ft.Padding(left=10, top=0, right=10, bottom=0),
                                                side=ft.BorderSide(1, c["azul_card"]),
                                            ),
                                            on_click=lambda e, tarea=t: confirmar_eliminacion(e, tarea),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=10,
                        ),
                    )
                )

    # ============================================================
    # Modal "Nueva tarea o recordatorio" (se construye una sola vez)
    # ============================================================
    def _construir_modal(c):
        # --- Campo de asunto ---
        tf_titulo_tarea = ft.TextField(
            hint_text="Asunto de la tarea o recordatorio",
            height=45, border_radius=30, bgcolor="#E9F5FF", color=c.get("borde_campo", "#A0C3FF"),
            text_size=18, hint_style=ft.TextStyle(color=ft.Colors.with_opacity(0.45, c.get("borde_campo", "#A0C3FF")), size=18),
            content_padding=ft.Padding.only(left=15), border_color=c.get("borde_campo", "#A0C3FF"),
            width=float("inf"),
        )
        lbl_campo_titulo = ft.Text("Asunto", size=18, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#004C95"))
        campo_titulo = ft.Container(
            content=ft.Column([lbl_campo_titulo, tf_titulo_tarea], spacing=4)
        )

        # --- Etiqueta de fecha y mensaje de error ---
        lbl_fecha_modal = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#89AEEA"))
        lbl_error_modal = ft.Text(
            "Es necesario rellenar el campo de asunto",
            color=c.get("text_red", "#E53935"),
            size=14,
            weight=ft.FontWeight.W_500,
            visible=False,
        )

        # --- Línea separadora decorativa (se estira para llenar todo el ancho) ---
        linea_separadora_modal = ft.Row(
            controls=[
                ft.Text("-", color="#09337F", size=12, weight=ft.FontWeight.BOLD)
                for _ in range(45)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=0,
            expand=True,
        )

        # --- Valida y guarda la nueva tarea ---
        def guardar_recordatorio(e):
            if tf_titulo_tarea.value and tf_titulo_tarea.value.strip():
                fecha_str = f"{fecha_activa['dia']}/{fecha_activa['mes']}/{fecha_activa['año']}"
                lista_tareas_data.append({"titulo": tf_titulo_tarea.value.strip(), "fecha": fecha_str})

                tf_titulo_tarea.value = ""
                lbl_error_modal.visible = False
                modal_recordatorio.open = False
                renderizar_tareas()

                # Al guardar, la burbuja seleccionada del calendario regresa a hoy
                resetear_calendario = fecha_activa.get("_resetear_calendario")
                if resetear_calendario:
                    resetear_calendario()

                page.update()
            else:
                lbl_error_modal.visible = True
                page.update()

        # --- Botón de guardar ---
        def _sombra_normal_modal():
            return ft.BoxShadow(blur_radius=10, spread_radius=1, color=colores().get("sombra", "#A9B8CE"), offset=ft.Offset(0, 3))

        def _sombra_hover_modal():
            return ft.BoxShadow(blur_radius=14, spread_radius=2, color=colores().get("sombra", "#A9B8CE"), offset=ft.Offset(0, 4))

        btn_guardar_recordatorio = ft.Container(
            content=ft.Text("Guardar recordatorio", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=15),
            bgcolor=c.get("boton_secundario", "#89AEEA"), border_radius=22, padding=8,
            shadow=_sombra_normal_modal(),
            alignment=ft.Alignment.CENTER, on_click=guardar_recordatorio, ink=True,
        )
        _aplicar_hover_boton(btn_guardar_recordatorio, _sombra_normal_modal, _sombra_hover_modal, escala_hover=1.03)

        # --- Botón circular de cerrar (regreso) ---
        def cerrar_modal_recordatorio():
            modal_recordatorio.open = False

            # Al cerrar sin guardar, la burbuja seleccionada del calendario regresa a hoy
            resetear_calendario = fecha_activa.get("_resetear_calendario")
            if resetear_calendario:
                resetear_calendario()

            page.update()

        btn_cerrar_modal = ft.Container(
            content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
            bgcolor=c.get("boton_secundario", "#89AEEA"), shape=ft.BoxShape.CIRCLE, padding=7,
            shadow=_sombra_normal_modal(),
            on_click=lambda e: cerrar_modal_recordatorio(), ink=True,
        )
        _aplicar_hover_boton(btn_cerrar_modal, _sombra_normal_modal, _sombra_hover_modal, escala_hover=1.1)

        txt_titulo_modal = ft.Text("Nueva tarea o recordatorio", size=28, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER)
        txt_subtitulo_modal = ft.Text("Ingresa los datos:", size=18, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER)

        # --- Encabezado del modal: botón de cerrar + título/subtítulo ---
        header_modal = ft.Row(
            [
                btn_cerrar_modal,
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [txt_titulo_modal, txt_subtitulo_modal],
                        spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    margin=ft.Margin.only(right=40)
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # --- Ensamblado del contenido del modal ---
        contenido_modal = ft.Container(
            width=650,
            height=340,
            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
            content=ft.Column(
                [
                    header_modal,
                    ft.Container(
                        content=ft.Column(
                            [
                                campo_titulo,
                                lbl_fecha_modal,
                                lbl_error_modal,
                                linea_separadora_modal,
                                btn_guardar_recordatorio,
                            ],
                            spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        margin=ft.Margin.only(top=15)
                    ),
                ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            )
        )

        # --- AlertDialog final ---
        modal_recordatorio = ft.AlertDialog(
            modal=True,
            content_padding=0,
            bgcolor=c.get("bg_card_white", ft.Colors.WHITE),
            shape=ft.RoundedRectangleBorder(radius=26),
            content=contenido_modal,
        )

        refs_modal = {
            "tf_titulo_tarea": tf_titulo_tarea,
            "lbl_campo_titulo": lbl_campo_titulo,
            "lbl_fecha_modal": lbl_fecha_modal,
            "lbl_error_modal": lbl_error_modal,
            "btn_cerrar_modal": btn_cerrar_modal,
            "btn_guardar_recordatorio": btn_guardar_recordatorio,
            "txt_titulo_modal": txt_titulo_modal,
            "txt_subtitulo_modal": txt_subtitulo_modal,
        }
        return modal_recordatorio, refs_modal

    modal_recordatorio, refs_modal = _construir_modal(colores())
    lbl_fecha_modal = refs_modal["lbl_fecha_modal"]
    page.overlay.append(modal_recordatorio)

    # --- Abre el modal, repintando sus colores con la paleta actual ---
    def abrir_modal_recordatorio(e):
        c = colores()
        modal_recordatorio.bgcolor = c.get("bg_card_white", ft.Colors.WHITE)
        refs_modal["btn_cerrar_modal"].bgcolor = c.get("boton_secundario", "#89AEEA")
        refs_modal["btn_cerrar_modal"].shadow = ft.BoxShadow(blur_radius=10, spread_radius=1, color=c.get("sombra", "#A9B8CE"), offset=ft.Offset(0, 3))
        refs_modal["txt_titulo_modal"].color = c.get("input_bg", "#183883")
        refs_modal["txt_subtitulo_modal"].color = c.get("input_bg", "#183883")
        refs_modal["lbl_campo_titulo"].color = c.get("input_bg", "#004C95")
        refs_modal["tf_titulo_tarea"].bgcolor = "#E9F5FF"
        refs_modal["tf_titulo_tarea"].border_color = c.get("borde_campo", "#A0C3FF")
        refs_modal["tf_titulo_tarea"].color = c.get("borde_campo", "#A0C3FF")
        refs_modal["lbl_fecha_modal"].color = c.get("input_bg", "#89AEEA")
        refs_modal["lbl_error_modal"].color = c.get("text_red", "#E53935")
        refs_modal["btn_guardar_recordatorio"].bgcolor = c.get("boton_secundario", "#89AEEA")
        refs_modal["btn_guardar_recordatorio"].shadow = ft.BoxShadow(blur_radius=10, spread_radius=1, color=c.get("sombra", "#A9B8CE"), offset=ft.Offset(0, 3))

        refs_modal["lbl_fecha_modal"].value = f"Para el día: {fecha_activa['dia']}/{fecha_activa['mes']}/{fecha_activa['año']}"
        modal_recordatorio.open = True
        page.update()

    # --- Botón "Agregar tarea" con el mismo efecto hover que la tarjeta de
    #     producto: borde en gradiente, ligero zoom y sombra más marcada ---
    def _crear_boton_agregar_tarea():
        c = colores()

        contenido_boton = ft.Container(
            bgcolor=c["boton_secundario"],
            border_radius=20,
            padding=ft.Padding.symmetric(vertical=10),
            alignment=ft.Alignment.CENTER,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=18),
                    ft.Text("Agregar tarea", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                tight=True,
            ),
        )

        boton_externo = ft.Container(
            width=500,
            border_radius=20,
            scale=1.0,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)),
            animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
            content=contenido_boton,
            on_click=abrir_modal_recordatorio,
            ink=True,
        )

        def al_pasar_mouse(e):
            esta_hover = str(e.data).lower() in ["true", "1"]

            if esta_hover:
                boton_externo.scale = 1.04
                boton_externo.shadow = ft.BoxShadow(
                    blur_radius=10,
                    spread_radius=1,
                    color=c.get("sombra", "#A9B8CE"),
                    offset=ft.Offset(0, 3),
                )
            else:
                boton_externo.scale = 1.0
                boton_externo.shadow = ft.BoxShadow(
                    spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)
                )

            boton_externo.update()

        boton_externo.on_hover = al_pasar_mouse

        return boton_externo

    # --- Tarjeta "TAREAS Y RECORDATORIOS" del dashboard ---
    def crear_tarjeta_tareas():
        c = colores()
        renderizar_tareas()
        return ft.Container(
            bgcolor=c["fondo_card"],
            border_radius=20,
            padding=15,
            expand=True,
            shadow=ft.BoxShadow(
                    blur_radius=10,
                    spread_radius=1,
                    color=c.get("sombra", "#A9B8CE"),
                    offset=ft.Offset(0, 3),
                ),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.DESCRIPTION, color=c["input_bg"], size=20),
                            ft.Text("TAREAS Y RECORDATORIOS", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=14),
                        ],
                        spacing=8,
                    ),
                    columna_tareas_list,
                    _crear_boton_agregar_tarea(),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
        )

    return {
        "crear_tarjeta_tareas": crear_tarjeta_tareas,
        "abrir_modal_recordatorio": abrir_modal_recordatorio,
        "obtener_lista": obtener_lista,
        "agregar_aviso": agregar_aviso,
    }