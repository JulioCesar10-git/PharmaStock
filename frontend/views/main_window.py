import flet as ft
import calendar
from datetime import datetime

# Variables globales para conservar el estado entre pestañas
ESTADO_FARMACIA = {
    "nombre": "Sin nombre asignado",
    "sucursal": "Sin sucursal asignada"
}

def main_window(page: ft.Page):
    page.title = "PharmaStock"
    page.window_width = 1100
    page.window_height = 700
    page.padding = 0

    nav_items_refs = []

    # Paleta de colores
    COLOR_AZUL_CARD = "#3B71E8"
    COLOR_INPUT_BG = "#0B2B63"
    COLOR_TEXTO_MUTED = "#D0E0FF"
    COLOR_BORDER = "#84ACFF"
    
    # Colores específicos del Dashboard "General"
    BG_CARD_BLUE = "#D3E4FF"       # Fondo tarjetas Calendario/Tareas/Ganancias
    BG_CARD_YELLOW = "#FBE2A8"     # Fondo tarjeta Avisos
    TEXT_RED = "#D32F2F"           # Texto alerta Avisos
    BG_CARD_WHITE = "#FFFFFF"

    titulo_seccion_text = ft.Text("General", size=24, weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG)

    # ----------------------------------------------------
    # COMPONENTES DEL DASHBOARD GENERAL
    # ----------------------------------------------------
    
    fecha_hoy = datetime.now()
    fecha_activa = {
        "dia": fecha_hoy.day,
        "mes": fecha_hoy.month,
        "año": fecha_hoy.year,
    }

    lista_tareas_data = [
    ]

    columna_tareas_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def renderizar_tareas():
    # 1. Función para mostrar la ventana emergente de confirmación
        def confirmar_eliminacion(e, tarea):
            # Función interna que ejecuta el borrado si se da clic en "Aceptar"
            def borrar_y_cerrar(e):
                lista_tareas_data.remove(tarea)
                modal_confirmacion.open = False
                renderizar_tareas()
                page.update()

            # Construimos el AlertDialog
            modal_confirmacion = ft.AlertDialog(
                title=ft.Text("Confirmar eliminación", color=COLOR_INPUT_BG, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"¿Estás seguro de que deseas marcar como completada y eliminar la tarea:\n\"{tarea['titulo']}\"?",
                    color=COLOR_INPUT_BG
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: setattr(modal_confirmacion, "open", False) or page.update()
                    ),
                    ft.ElevatedButton(
                        "Aceptar",
                        bgcolor=TEXT_RED,
                        color=ft.Colors.WHITE,
                        on_click=borrar_y_cerrar
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            # Agregamos el diálogo a la pantalla y lo abrimos
            page.overlay.append(modal_confirmacion)
            modal_confirmacion.open = True
            page.update()

        columna_tareas_list.controls.clear()
        
        if not lista_tareas_data:
            columna_tareas_list.controls.append(
                ft.Text("No hay recordatorios pendientes", color=COLOR_INPUT_BG, italic=True)
            )
        else:
            for t in lista_tareas_data:
                columna_tareas_list.controls.append(
                    ft.Container(
                        bgcolor=BG_CARD_WHITE,
                        border_radius=10,
                        padding=12,
                        content=ft.Column([
                            # Título con ancho disponible
                            ft.Text(
                                t["titulo"],
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_INPUT_BG,
                            ),
                            
                            # Fila inferior: Fecha a la izquierda, Botón a la derecha
                            ft.Row([
                                ft.Text(
                                    t["fecha"],
                                    size=12,
                                    color=COLOR_AZUL_CARD,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.ElevatedButton(
                                    "Completada",
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    bgcolor="#E3F2FD",
                                    color=COLOR_AZUL_CARD,
                                    icon_color=COLOR_AZUL_CARD,
                                    elevation=0,
                                    height=32,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding(left=10, top=0, right=10, bottom=0)
                                    ),
                                    # Ahora llama a la función de confirmación
                                    on_click=lambda e, tarea=t: confirmar_eliminacion(e, tarea)
                                ),
                            ], 
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ], spacing=10)
                    )
                )

    tf_titulo_tarea = ft.TextField(
        label="Asunto de la tarea o recordatorio", 
        border_color=COLOR_AZUL_CARD
    )
    lbl_fecha_modal = ft.Text("", weight=ft.FontWeight.BOLD, color=COLOR_AZUL_CARD)
    
    # Texto de error inicialmente oculto (visible=False)
    lbl_error_modal = ft.Text(
        "Es necesario rellenar el campo de asunto", 
        color=TEXT_RED, 
        size=12, 
        weight=ft.FontWeight.W_500,
        visible=False
    )

    def guardar_recordatorio(e):
        if tf_titulo_tarea.value and tf_titulo_tarea.value.strip():
            fecha_str = f"{fecha_activa['dia']}/{fecha_activa['mes']}/{fecha_activa['año']}"
            lista_tareas_data.append(
                {"titulo": tf_titulo_tarea.value.strip(), "fecha": fecha_str}
            )

            tf_titulo_tarea.value = ""
            lbl_error_modal.visible = False  # Ocultamos el mensaje
            modal_recordatorio.open = False
            renderizar_tareas()
            page.update()
        else:
            # Mostramos el mensaje en rojo
            lbl_error_modal.visible = True
            page.update()

    modal_recordatorio = ft.AlertDialog(
        title=ft.Text("Nueva tarea o recordatorio", color=COLOR_INPUT_BG, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                lbl_fecha_modal,
                tf_titulo_tarea,
                lbl_error_modal, # Agregado a la columna
            ],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: setattr(modal_recordatorio, "open", False) or page.update(),
            ),
            ft.ElevatedButton(
                "Guardar",
                bgcolor=COLOR_AZUL_CARD,
                color=ft.Colors.WHITE,
                on_click=guardar_recordatorio,
            ),
        ],
    )
    page.overlay.append(modal_recordatorio)

    def abrir_modal_recordatorio(e):
        lbl_fecha_modal.value = f"Para el día: {fecha_activa['dia']}/{fecha_activa['mes']}/{fecha_activa['año']}"
        modal_recordatorio.open = True
        page.update()

    # 1. Tarjeta de Calendario (Columna 1 Arriba)
    def crear_tarjeta_calendario():
        fecha_actual = datetime.now()
        estado_fecha = {
            "año": fecha_actual.year,
            "mes": fecha_actual.month,
            "dia_seleccionado": fecha_actual.day
        }

        meses_es = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        lbl_mes = ft.Text(meses_es[estado_fecha["mes"] - 1], weight=ft.FontWeight.BOLD, color=COLOR_AZUL_CARD)
        lbl_año = ft.Text(str(estado_fecha["año"]), weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG)
        grid_container = ft.Column(key="grid_calendario_clean", spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def seleccionar_dia(e, dia):
            estado_fecha["dia_seleccionado"] = dia
            fecha_activa["dia"] = dia
            fecha_activa["mes"] = estado_fecha["mes"]
            fecha_activa["año"] = estado_fecha["año"]
            renderizar_matriz_dias()
            abrir_modal_recordatorio(e)

        def renderizar_matriz_dias():
            grid_container.controls.clear()
            dias_semana = ["Dom", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]
            hdr_row = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(d, size=10, weight=ft.FontWeight.BOLD, color="grey", text_align=ft.TextAlign.CENTER),
                        width=28, alignment=ft.Alignment.CENTER
                    ) for d in dias_semana
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4
            )
            grid_container.controls.append(hdr_row)
            cal = calendar.Calendar(firstweekday=6)
            dias_mes = cal.monthdayscalendar(estado_fecha["año"], estado_fecha["mes"])

            for semana in dias_mes:
                fila_controles = []
                for dia in semana:
                    if dia == 0:
                        fila_controles.append(ft.Container(width=28, height=28))
                    else:
                        es_seleccionado = (dia == estado_fecha["dia_seleccionado"])

                        btn_dia = ft.Container(
                            content=ft.Text(
                                str(dia),
                                size=11,
                                weight=ft.FontWeight.BOLD if es_seleccionado else ft.FontWeight.NORMAL,
                                color=ft.Colors.WHITE if es_seleccionado else COLOR_INPUT_BG,
                                text_align=ft.TextAlign.CENTER
                            ),
                            width=28,
                            height=28,
                            border_radius=14,
                            bgcolor=COLOR_AZUL_CARD if es_seleccionado else None,
                            alignment=ft.Alignment.CENTER,
                            ink=True,
                            on_click=lambda e, d=dia: seleccionar_dia(e, d)
                        )
                        fila_controles.append(btn_dia)
                    
                grid_container.controls.append(
                    ft.Row(controls=fila_controles, alignment=ft.MainAxisAlignment.CENTER, spacing=4)
                )

        def mes_anterior(e):
            if estado_fecha["mes"] == 1:
                estado_fecha["mes"] = 12
                estado_fecha["año"] -= 1
            else:
                estado_fecha["mes"] -= 1

            lbl_mes.value = meses_es[estado_fecha["mes"] - 1]
            lbl_año.value = str(estado_fecha["año"])
            renderizar_matriz_dias()
            page.update()

        def mes_siguiente(e):
            if estado_fecha["mes"] == 12:
                estado_fecha["mes"] = 1
                estado_fecha["año"] += 1
            else:
                estado_fecha["mes"] += 1

            lbl_mes.value = meses_es[estado_fecha["mes"] - 1]
            lbl_año.value = str(estado_fecha["año"])
            renderizar_matriz_dias()
            page.update()

        renderizar_matriz_dias()

        return ft.Container(
            bgcolor=BG_CARD_BLUE,
            border_radius=15,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=COLOR_INPUT_BG, size=20),
                    ft.Text("CALENDARIO", weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG, size=14)
                ], spacing=8),

                ft.Container(
                    bgcolor=BG_CARD_WHITE,
                    border_radius=10,
                    padding=10,
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_LEFT, 
                                icon_size=18, 
                                icon_color=COLOR_AZUL_CARD,
                                on_click=mes_anterior,
                                padding=0
                            ),
                            lbl_mes,
                            ft.IconButton(
                                icon=ft.Icons.ARROW_RIGHT, 
                                icon_size=18, 
                                icon_color=COLOR_AZUL_CARD,
                                on_click=mes_siguiente,
                                padding=0
                            ),
                            ft.Container(expand=True),
                            lbl_año
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(height=5, color="transparent"),
                        grid_container
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ])
        )

    # 2. Tarjeta de Ganancias (Columna 1 Abajo)
    def crear_tarjeta_ganancias():
        return ft.Container(
            bgcolor=BG_CARD_BLUE,
            border_radius=15,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MONETIZATION_ON, color=COLOR_INPUT_BG, size=20),
                    ft.Text("GANANCIAS", weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG, size=14)
                ], spacing=8),
                ft.Container(
                    bgcolor=BG_CARD_WHITE,
                    border_radius=10,
                    padding=15,
                    height=180,
                    content=ft.Column([
                        ft.Text("20 K ---", size=10, color="grey"),
                        ft.Text("15 K ---", size=10, color="grey"),
                        ft.Text("10 K ---", size=10, color="grey"),
                        ft.Container(expand=True),
                        ft.Row([
                            ft.Text("MAY", size=10), ft.Text("JUN", size=10),
                            ft.Text("JUL", size=10), ft.Text("AGO", size=10), ft.Text("SEP", size=10)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
            ])
        )

    # 3. Tarjeta de Tareas (Columna 2)
    def crear_tarjeta_tareas():
        renderizar_tareas()
        return ft.Container(
            bgcolor=BG_CARD_BLUE,
            border_radius=15,
            padding=15,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DESCRIPTION, color=COLOR_INPUT_BG, size=20),
                    ft.Text("TAREAS Y RECORDATORIOS", weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG, size=14)
                ], spacing=8),
                columna_tareas_list,
                ft.ElevatedButton(
                    "+ Agregar Tarea",
                    bgcolor="#6F8EB9",
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    width=500,
                    on_click=abrir_modal_recordatorio
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
        )

    # 4. Componentes de Avisos (Columna 3)
    def crear_item_aviso_caducidad(medicamento, fecha):
        return ft.Container(
            bgcolor=BG_CARD_WHITE,
            border_radius=10,
            padding=12,
            content=ft.Column([
                ft.Text("Próximo a caducar", color=TEXT_RED, weight=ft.FontWeight.W_500, size=13),
                ft.Container(
                    height=90,
                    border=ft.Border.all(1.5, COLOR_AZUL_CARD),
                    border_radius=5,
                    content=ft.Icon(ft.Icons.MEDICATION, color=COLOR_AZUL_CARD, size=40),
                    alignment=ft.Alignment.CENTER
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Text(medicamento, size=10, color=TEXT_RED),
                        bgcolor="#FCE4EC",
                        padding=ft.Padding.all(4),
                        border_radius=5
                    ),
                    ft.Container(
                        content=ft.Text("Fracción 1", size=10, color=TEXT_RED),
                        bgcolor="#FCE4EC",
                        padding=ft.Padding.all(4),
                        border_radius=5
                    )
                ]),
                ft.Row([
                    ft.Text("Fecha de caducidad", size=11, color=TEXT_RED),
                    ft.Container(expand=True),
                    ft.Text(fecha, size=11, color=TEXT_RED, weight=ft.FontWeight.BOLD)
                ])
            ], spacing=8)
        )
    
    def crear_texto_aviso_general(titulo):
        return ft.Container(
            bgcolor=BG_CARD_WHITE,
            border_radius=10,
            padding=12,
            content=ft.Row([
                ft.Text(titulo, weight=ft.FontWeight.W_500, color=TEXT_RED, size=14),
            ])
        )

    # 5. Tarjeta de Avisos con SCROLL (Columna 3)
    def crear_tarjeta_avisos():
        return ft.Container(
            bgcolor=BG_CARD_YELLOW,
            border_radius=15,
            padding=15,
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=TEXT_RED, size=20),
                    ft.Text("AVISOS", weight=ft.FontWeight.BOLD, color=TEXT_RED, size=14)
                ], spacing=8),
                
                ft.Column(
                    controls=[
                        crear_texto_aviso_general("Avisos generales del sistema aparecerán aquí."),
                        crear_item_aviso_caducidad("Amoxicilina 500mg", "15/11/2026"),
                        crear_item_aviso_caducidad("Ibuprofeno 400mg", "02/12/2026"),
                    ],
                    scroll=ft.ScrollMode.ALWAYS,
                    expand=True,
                    spacing=12
                )
            ])
        )

    # --- VISTA GENERAL ENSAMBLADA ---
    def vista_general(page: ft.Page):
        return ft.Row([
            # Columna 1: Calendario + Ganancias
            ft.Column([
                crear_tarjeta_calendario(),
                crear_tarjeta_ganancias()
            ], expand=1, scroll=ft.ScrollMode.AUTO),

            # Columna 2: Tareas
            ft.Column([
                crear_tarjeta_tareas()
            ], expand=1),

            # Columna 3: Avisos con Scroll
            ft.Column([
                crear_tarjeta_avisos()
            ], expand=1)
        ], spacing=15, expand=True)

    # ----------------------------------------------------
    # NAVEGACIÓN Y ESTRUCTURA GENERAL
    # ----------------------------------------------------
    def nav_item(icon, texto, key, activo=False):
        icono_ctrl = ft.Icon(icon, color=ft.Colors.WHITE if activo else COLOR_AZUL_CARD, size=22)
        texto_ctrl = ft.Text(texto, color=ft.Colors.WHITE if activo else COLOR_AZUL_CARD, weight=ft.FontWeight.BOLD if activo else ft.FontWeight.W_500)

        item = ft.Container(
            content=ft.Row([icono_ctrl, texto_ctrl], spacing=10),
            bgcolor=COLOR_AZUL_CARD if activo else None,
            border_radius=30,
            padding=ft.Padding(left=15, top=12, right=15, bottom=12),
            width=200,
            data=key,           
            on_click=cambiar_seccion,
            ink=True,           
        )

        nav_items_refs.append({"container": item, "icono": icono_ctrl, "texto": texto_ctrl, "key": key})
        return item
    
    # ----------------------------------------------------
    # COMPONENTES Y VISTA DEL INVENTARIO
    # ----------------------------------------------------
    def crear_tarjeta_producto(nombre, categoria, precio, stock, alertas=[]):
        # 1. Placeholder de la imagen (recuadro azul claro)
        imagen_placeholder = ft.Container(
            height=140,
            bgcolor="#E8F1FF",
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
            border=ft.Border.all(1, "#A0C3FF"),
            content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color="#A0C3FF", size=40),
            alignment=ft.Alignment.CENTER,
        )

        # 2. Insignias de Alertas (Stock bajo / Caducidad) en la esquina superior derecha
        alertas_column = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(alerta, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor="#E53935",
                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                    border_radius=12,
                ) for alerta in alertas
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.END,
        )

        # Stack para superponer las alertas sobre la imagen
        header_stack = ft.Stack(
            controls=[
                imagen_placeholder,
                ft.Container(
                    content=alertas_column,
                    top=6,
                    right=6,
                )
            ]
        )

        # 3. Cuerpo con información del medicamento
        info_container = ft.Container(
            padding=12,
            content=ft.Column([
                # Categoría y Precio
                ft.Row([
                    ft.Container(
                        content=ft.Text(categoria, size=11, color="#2B529A", weight=ft.FontWeight.W_500),
                        bgcolor="#E8F1FF",
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=12,
                    ),
                    ft.Text(f"${precio}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Nombre del medicamento
                ft.Text(nombre, size=15, weight=ft.FontWeight.BOLD, color=COLOR_INPUT_BG),
                
                # Cantidad en stock
                ft.Text(f"En almacén: {stock} pz", size=12, color="grey")
            ], spacing=6)
        )

        return ft.Container(
            bgcolor=BG_CARD_WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)),
            content=ft.Column([header_stack, info_container], spacing=0)
        )

    def vista_inventario(page: ft.Page):

        bar_busqueda = ft.Row([
                    ft.TextField(
                        hint_text="Buscar",
                        prefix_icon=ft.Icons.SEARCH,
                        height=40,
                        border_radius=20,
                        content_padding=ft.Padding.only(left=10, right=10),
                        border_color="#A0C3FF",
                        expand=True
                    ),
                    ft.ElevatedButton("+ Añadir", bgcolor="#89AEEA", color=ft.Colors.WHITE, height=38),
                    ft.ElevatedButton("Y Filtros", icon=ft.Icons.FILTER_ALT, bgcolor="#89AEEA", color=ft.Colors.WHITE, height=38),
                    ft.ElevatedButton("Ordenar", icon=ft.Icons.GRID_VIEW, bgcolor="#89AEEA", color=ft.Colors.WHITE, height=38),
                ], spacing=10)
        
        # ----------------------------------------------------
        # LÓGICA DE FARMACIA Y SUCURSAL
        # ----------------------------------------------------
        # --- 1. EDITAR NOMBRE DE LA FARMACIA ---
        # Leemos el valor guardado en el estado global
        texto_nombre_farmacia = ft.Text(
            ESTADO_FARMACIA["nombre"], 
            size=18, 
            weight=ft.FontWeight.BOLD, 
            color=COLOR_INPUT_BG
        )
        
        tf_nuevo_nombre_farmacia = ft.TextField(
            label="Nombre de la farmacia", 
            hint_text="Ej. Farmacia San Martín", 
            max_length=30,
            autofocus=True
        )

        def cerrar_dialogo_farmacia(e):
            dialogo_farmacia.open = False
            page.update()

        def guardar_nombre_farmacia(e):
            if tf_nuevo_nombre_farmacia.value and tf_nuevo_nombre_farmacia.value.strip():
                nuevo_val = tf_nuevo_nombre_farmacia.value.strip()
                # 1. Actualizamos la variable de estado persistente
                ESTADO_FARMACIA["nombre"] = nuevo_val
                # 2. Actualizamos la interfaz actual
                texto_nombre_farmacia.value = nuevo_val
            cerrar_dialogo_farmacia(e)

        dialogo_farmacia = ft.AlertDialog(
            title=ft.Text("Editar Nombre de la Farmacia"),
            content=tf_nuevo_nombre_farmacia,
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo_farmacia),
                ft.ElevatedButton(
                    "Guardar", 
                    bgcolor="#89AEEA", 
                    color=ft.Colors.WHITE, 
                    on_click=guardar_nombre_farmacia
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if dialogo_farmacia not in page.overlay:
            page.overlay.append(dialogo_farmacia)

        def abrir_dialogo_farmacia(e):
            # Cargar el valor del estado persistente en el TextField
            valor_actual = ESTADO_FARMACIA["nombre"]
            tf_nuevo_nombre_farmacia.value = "" if valor_actual == "Sin nombre asignado" else valor_actual
            
            dialogo_farmacia.open = True
            page.update()

        # --- 2. EDITAR SUCURSAL ---
        texto_sucursal = ft.Text(
            f"Sucursal: {ESTADO_FARMACIA['sucursal']}", 
            size=11, 
            color="#3B71E8"
        )
        
        tf_nueva_sucursal = ft.TextField(
            label="Nombre o dirección de la sucursal", 
            hint_text="Ej. Avenida Cuitlahuac 30 A", 
            autofocus=True
        )

        def cerrar_dialogo_sucursal(e):
            dialogo_sucursal.open = False
            page.update()

        def guardar_nombre_sucursal(e):
            if tf_nueva_sucursal.value and tf_nueva_sucursal.value.strip():
                nuevo_val = tf_nueva_sucursal.value.strip()
                # Actualizamos la variable de estado persistente
                ESTADO_FARMACIA["sucursal"] = nuevo_val
                texto_sucursal.value = f"Sucursal: {nuevo_val}"
            cerrar_dialogo_sucursal(e)

        dialogo_sucursal = ft.AlertDialog(
            title=ft.Text("Editar Sucursal"),
            content=tf_nueva_sucursal,
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo_sucursal),
                ft.ElevatedButton(
                    "Guardar", 
                    bgcolor="#89AEEA", 
                    color=ft.Colors.WHITE, 
                    on_click=guardar_nombre_sucursal
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if dialogo_sucursal not in page.overlay:
            page.overlay.append(dialogo_sucursal)

        def abrir_dialogo_sucursal(e):
            valor_actual = ESTADO_FARMACIA["sucursal"]
            tf_nueva_sucursal.value = "" if valor_actual == "Sin sucursal asignada" else valor_actual
            
            dialogo_sucursal.open = True
            page.update()


        # --- 2. EDITAR SUCURSAL ---
        texto_sucursal = ft.Text("Sucursal: Sin sucursal asignada", size=11, color="#3B71E8")
        tf_nueva_sucursal = ft.TextField(
            label="Nombre o dirección de la sucursal", 
            hint_text="Ej. Avenida Cuitlahuac 30 A", 
            autofocus=True
        )

        def cerrar_dialogo_sucursal(e):
            dialogo_sucursal.open = False
            page.update()

        def guardar_nombre_sucursal(e):
            if tf_nueva_sucursal.value.strip():
                texto_sucursal.value = f"Sucursal: {tf_nueva_sucursal.value.strip()}"
            cerrar_dialogo_sucursal(e)

        dialogo_sucursal = ft.AlertDialog(
            title=ft.Text("Editar Sucursal"),
            content=tf_nueva_sucursal,
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo_sucursal),
                ft.ElevatedButton(
                    "Guardar", 
                    bgcolor="#89AEEA", 
                    color=ft.Colors.WHITE, 
                    on_click=guardar_nombre_sucursal
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def abrir_dialogo_sucursal(e):
            valor_actual = texto_sucursal.value.replace("Sucursal: ", "")
            tf_nueva_sucursal.value = valor_actual if valor_actual != "Sin sucursal asignada" else ""
            # Sintaxis correcta para Flet 0.86:
            page.dialog = dialogo_sucursal
            dialogo_sucursal.open = True
            page.update()

        # --- 3. ENSAMBLADO DEL ENCABEZADO ---
        header_farmacia = ft.Row([
            # Sección izquierda: Farmacia y Badges
            ft.Row([
                ft.Icon(ft.Icons.STORE, color=COLOR_INPUT_BG, size=24),
                texto_nombre_farmacia,
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color="#2B529A",
                    tooltip="Editar farmacia",
                    icon_size=18,
                    on_click=abrir_dialogo_farmacia
                ),
                ft.Container(
                    content=ft.Text("50 productos | 500 medicamentos", size=11, color="#3B71E8", weight=ft.FontWeight.BOLD),
                    bgcolor="#D0E0FF",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    border_radius=12
                )
            ], spacing=4),

            # Sección derecha: Sucursal y su botón de edición
            ft.Row([
                texto_sucursal,
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color="#3B71E8",
                    tooltip="Editar sucursal",
                    icon_size=16,
                    on_click=abrir_dialogo_sucursal
                ),
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # D) Paginación Inferior
        paginacion = ft.Row([
            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_LEFT, icon_color=COLOR_AZUL_CARD, bgcolor="#D0E0FF"),
            ft.Container(content=ft.Text("1", color=ft.Colors.WHITE), bgcolor=COLOR_AZUL_CARD, border_radius=15, padding=ft.Padding.symmetric(horizontal=12, vertical=6)),
            ft.Text("2", color=COLOR_INPUT_BG),
            ft.Text("3", color=COLOR_INPUT_BG),
            ft.Text(".", color=COLOR_INPUT_BG),
            ft.Text(".", color=COLOR_INPUT_BG),
            ft.Text("5", color=COLOR_INPUT_BG),
            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_RIGHT, icon_color=COLOR_AZUL_CARD, bgcolor="#D0E0FF"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        # Ensamble de la Vista completa
        return ft.Container(
            bgcolor="#EBF3FF",
            border_radius=15,
            padding=20,
            expand=True,
            content=ft.Column([
                bar_busqueda,
                header_farmacia,
                ft.Divider(color="#A0C3FF", height=1),
                paginacion
            ], spacing=15, expand=True)
        )

    def cambiar_seccion(e):
        key_clickeado = e.control.data

        for ref in nav_items_refs:
            activo = ref["key"] == key_clickeado
            ref["container"].bgcolor = COLOR_AZUL_CARD if activo else None
            ref["icono"].color = ft.Colors.WHITE if activo else COLOR_AZUL_CARD
            ref["texto"].color = ft.Colors.WHITE if activo else COLOR_AZUL_CARD

        titulo_seccion_text.value = key_clickeado

        # LÓGICA DE CAMBIO DE VISTA
        if key_clickeado == "General":
            area_dinamica.content = vista_general(page)
        elif key_clickeado == "Inventario":
            area_dinamica.content = vista_inventario(page)
        else:
            area_dinamica.content = ft.Text(f"Contenido de {key_clickeado}", size=18, color=COLOR_AZUL_CARD)

        page.update()

    top_bar = ft.Container(
        padding=ft.Padding.only(left=30, top=15, right=30, bottom=15),
        content=ft.Row([
            titulo_seccion_text,
            ft.Row([
                ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=COLOR_AZUL_CARD),
                ft.Container(
                    width=36, height=36, border_radius=18, bgcolor=COLOR_INPUT_BG,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.PERSON_OUTLINED, color=ft.Colors.WHITE, size=20)
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    menu_lateral = ft.Container(
        width=250, bgcolor=ft.Colors.WHITE, padding=20,
        content=ft.Column([
            ft.Text("PHARMASTOCK", size=18, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_CARD),
            ft.Divider(color=ft.Colors.BLUE_GREY_100),
            ft.Column([
                nav_item(ft.Icons.HOME, "General", key="General", activo=True),
                nav_item(ft.Icons.INVENTORY_2, "Inventario", key="Inventario"),
                nav_item(ft.Icons.PEOPLE, "Empleados", key="Empleados"),
                nav_item(ft.Icons.DESCRIPTION, "Reportes", key="Reportes"),
                nav_item(ft.Icons.LOCAL_SHIPPING, "Proveedores", key="Proveedores"),
            ], spacing=8),
            ft.Container(expand=True),
            nav_item(ft.Icons.SETTINGS, "Ajustes", key="Ajustes"),
        ])
    )

    area_dinamica = ft.Container(
        content=vista_general(page), padding=20, expand=True, bgcolor="#F4F8FE")

    contenido_principal = ft.Column(
        [top_bar, area_dinamica], spacing=0, expand=True)

    page.add(
        ft.Row([menu_lateral, contenido_principal], expand=True, spacing=0))

if __name__ == "__main__":
    ft.app(target=main_window)