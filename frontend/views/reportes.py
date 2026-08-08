import math
import asyncio
from datetime import datetime
import calendar
import copy
import flet as ft

from theme import colores
from state import PRODUCTOS_GLOBALES, PROVEEDORES_GLOBALES, ESTADO_UI

REPORTES_POR_PAGINA = 7
MAX_PAGINAS_VISIBLES = 5
ANCHO_PAGINADOR_NUMEROS = 480

# --- Aplica el mismo efecto hover (zoom + sombra más marcada) que el
#     botón "Agregar tarea" de recordatorios.py, a un Container-botón ---
def _aplicar_hover_boton_paginacion(boton, sombra_normal, sombra_hover, escala_hover=1.10):
    boton.scale = 1.0
    boton.shadow = sombra_normal
    boton.animate_scale = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)
    boton.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)

    def _al_pasar_mouse(e):
        esta_hover = str(e.data).lower() in ["true", "1"]
        if esta_hover and not boton.disabled:
            boton.scale = escala_hover
            boton.shadow = sombra_hover
        else:
            boton.scale = 1.0
            boton.shadow = sombra_normal
        boton.update()

    boton.on_hover = _al_pasar_mouse

# --- Configuración de columnas de la tabla ---
COLUMNAS = [
    ("NO.", 1),
    ("Nombre", 2),
    ("Última modificación", 2),
    ("Productos", 1),
    ("Medicamentos", 1),
    ("Total", 1),
]
EXPAND_ACCIONES = 1


_REPORTES_GLOBALES = None

# --- Filtra una lista de proveedores para dejar solo los que siguen existiendo
#     en la pestaña de Proveedores (PROVEEDORES_GLOBALES) y sin nombres repetidos ---
def _proveedores_validos_sin_duplicados(lista_proveedores):
    nombres_validos = {(p.get("nombre") or "").strip().lower() for p in PROVEEDORES_GLOBALES}
    vistos = set()
    resultado = []
    for prov in lista_proveedores:
        nombre = (prov.get("nombre") or "").strip()
        clave = nombre.lower()
        if clave and clave in nombres_validos and clave not in vistos:
            vistos.add(clave)
            resultado.append(prov)
    return resultado

# --- Calcula qué números de página mostrar en el paginador ---
def _generar_paginas_visibles(pagina_actual, total_paginas, max_visibles=MAX_PAGINAS_VISIBLES):
    if total_paginas <= max_visibles:
        return list(range(1, total_paginas + 1))

    inicio_ventana = max(1, min(pagina_actual - (max_visibles - 2), total_paginas - max_visibles + 1))
    fin_ventana = min(total_paginas, inicio_ventana + max_visibles - 1)

    paginas = list(range(inicio_ventana, fin_ventana + 1))

    if paginas[0] > 1:
        paginas = ([1, "..."] if paginas[0] > 2 else [1]) + paginas

    if paginas[-1] < total_paginas:
        paginas = paginas + (["...", total_paginas] if paginas[-1] < total_paginas - 1 else [total_paginas])

    return paginas

# --- Datos de ejemplo / acceso a la lista global de reportes ---
MESES_ABREV = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_NOMBRE = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]

def _generar_reportes_ejemplo():
    # Un reporte de ejemplo por cada mes de 2026 y de 2025 (24 en total),
    # del más reciente al más antiguo.
    reportes = []
    no = 1
    for anio in (2026, 2025):
        for mes in range(12, 0, -1):
            if anio == 2026 and mes in (9, 10, 11, 12):
                continue
            ultimo_dia = calendar.monthrange(anio, mes)[1]
            nombre_mes = MESES_NOMBRE[mes - 1]
            fecha_str = f"{MESES_ABREV[mes - 1]} {ultimo_dia}, {anio}"

            productos_lista = [{"producto": p, "piezas": 5} for p in PRODUCTOS_GLOBALES]
            productos_count = sum(
                item["piezas"] for item in productos_lista if item["producto"].get("tipo") != "Medicamento"
            )
            medicamentos_count = sum(
                item["piezas"] for item in productos_lista if item["producto"].get("tipo") == "Medicamento"
            )
            total_monto = sum(item["piezas"] * item["producto"].get("precio", 0.0) for item in productos_lista)

            reportes.append(
                {
                    "no": no,
                    "nombre": f"VENTAS_{nombre_mes}_{anio}",
                    "fecha": fecha_str,
                    "productos": productos_count,
                    "medicamentos": medicamentos_count,
                    "total": total_monto,
                    "productos_lista": productos_lista,
                    "proveedores_lista": _proveedores_validos_sin_duplicados(copy.deepcopy(PROVEEDORES_GLOBALES)),
                }
            )
            no += 1
    return reportes

def _obtener_reportes():
    global _REPORTES_GLOBALES
    if _REPORTES_GLOBALES is None:
        _REPORTES_GLOBALES = _generar_reportes_ejemplo()
    return _REPORTES_GLOBALES

# --- Suma el "total" de los reportes de ventas de cada mes de un año dado ---
# Usado por la tarjeta de GANANCIAS para graficar datos reales (se refleja
# cualquier reporte agregado/editado/eliminado, ya que lee la misma lista global).
def obtener_anios_disponibles():
    reportes = _obtener_reportes()
    return sorted({r["nombre"].split("_")[-1] for r in reportes}, reverse=True)

def obtener_ganancias_por_mes(anio):
    reportes = _obtener_reportes()
    totales = {mes: 0.0 for mes in range(1, 13)}
    for r in reportes:
        partes = (r.get("nombre") or "").split("_")
        if len(partes) < 3:
            continue
        nombre_mes = partes[1]
        anio_reporte = partes[-1]
        if anio_reporte != str(anio):
            continue
        if nombre_mes in MESES_NOMBRE:
            mes_num = MESES_NOMBRE.index(nombre_mes) + 1
            totales[mes_num] += r.get("total", 0.0)
    return totales

# --- Helpers de UI reutilizables ---
def _linea_punteada(color, caracter="·", size=16):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(-1, 0),
        content=ft.Text(
            caracter * 200,
            color=color,
            size=size,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

def _encabezado_seccion_dialogo(titulo, color):
    return ft.Row(
        controls=[
            _linea_punteada(color=color, caracter="-", size=12),
            ft.Text(titulo, weight=ft.FontWeight.BOLD, color=color, size=14),
            _linea_punteada(color=color, caracter="-", size=12),
        ],
        spacing=15,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

# --- Fila de encabezado de la tabla de reportes ---
def _fila_encabezado_tabla(c):
    return ft.Container(
        bgcolor=c["fondo_lienzo"],
        border_radius=30,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Row(
            [
                ft.Container(
                    expand=ancho,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(texto, size=12, weight=ft.FontWeight.BOLD, color=c["input_bg"], text_align=ft.TextAlign.CENTER),
                )
                for texto, ancho in COLUMNAS
            ] + [ft.Container(expand=EXPAND_ACCIONES)],
        ),
    )

# --- Fila individual de la tabla con acciones de editar/eliminar ---
def _fila_reporte(reporte, on_editar, on_eliminar, c):
    valores = [f"{reporte['no']:02d}", reporte["nombre"], reporte["fecha"], str(reporte["productos"]), str(reporte.get("medicamentos", 0)), f"${reporte['total']}"]
    colores_texto = [c["input_bg"], c["input_bg"], c["texto_secundario"], c["input_bg"], c["input_bg"], c["input_bg"]]
    pesos = [ft.FontWeight.NORMAL, ft.FontWeight.BOLD, ft.FontWeight.NORMAL, ft.FontWeight.NORMAL, ft.FontWeight.NORMAL, ft.FontWeight.BOLD]

    celdas = [
        ft.Container(
            expand=ancho,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(valor, size=13, color=color, weight=peso, text_align=ft.TextAlign.CENTER),
        )
        for (_, ancho), valor, color, peso in zip(COLUMNAS, valores, colores_texto, pesos)
    ]

    celdas.append(
        ft.Container(
            expand=EXPAND_ACCIONES,
            alignment=ft.Alignment(0, 0),
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=18, color="#1E88E5"),
                        bgcolor=c["bg_card_white"],
                        shape=ft.BoxShape.CIRCLE,
                        padding=9,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color="#C2D1EB", offset=ft.Offset(0, 1)),
                        on_click=lambda e, r=reporte: on_editar(r),
                        tooltip="Editar",
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE, size=18, color="#E53935"),
                        bgcolor=c["bg_card_white"],
                        shape=ft.BoxShape.CIRCLE,
                        padding=9,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color="#C2D1EB", offset=ft.Offset(0, 1)),
                        on_click=lambda e, r=reporte: on_eliminar(r),
                        tooltip="Eliminar",
                        ink=True,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
    )

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        border=ft.Border(bottom=ft.BorderSide(1, c["divisor"])),
        content=ft.Row(celdas, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

# ============================================================
# Vista: editar reporte de ventas (proveedores y productos incluidos)
# ============================================================
def _construir_vista_editar_reporte(page: ft.Page, reporte, al_regresar_callback):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    productos_seleccionados = copy.deepcopy(reporte.setdefault("productos_lista", []))
    proveedores_seleccionados = copy.deepcopy(reporte.setdefault("proveedores_lista", []))

    temp_productos_count = reporte.get("productos", 0)
    temp_medicamentos_count = reporte.get("medicamentos", 0)
    temp_total_monto = reporte.get("total", 0.0)

    meses_espanol = {
        "ENE": "Enero", "FEB": "Febrero", "MAR": "Marzo", "ABR": "Abril",
        "MAY": "Mayo", "JUN": "Junio", "JUL": "Julio", "AGO": "Agosto",
        "SEP": "Septiembre", "OCT": "Octubre", "NOV": "Noviembre", "DIC": "Diciembre",
        "ENERO": "Enero", "FEBRERO": "Febrero", "MARZO": "Marzo", "ABRIL": "Abril",
        "MAYO": "Mayo", "JUNIO": "Junio", "JULIO": "Julio", "AGOSTO": "Agosto",
        "SEPTIEMBRE": "Septiembre", "OCTUBRE": "Octubre", "NOVIEMBRE": "Noviembre", "DICIEMBRE": "Diciembre"
    }

    mes_encontrado = "Julio"
    anio_encontrado = "2026"

    try:
        partes_nombre = reporte["nombre"].split("_")
        if len(partes_nombre) >= 3:
            m_key = partes_nombre[1].upper()
            if m_key in meses_espanol:
                mes_encontrado = meses_espanol[m_key]
            anio_encontrado = partes_nombre[2]
        else:
            partes_fecha = reporte["fecha"].replace(",", "").split()
            if len(partes_fecha) >= 3:
                m_key = partes_fecha[0].upper()
                if m_key in meses_espanol:
                    mes_encontrado = meses_espanol[m_key]
                anio_encontrado = partes_fecha[2]
    except Exception:
        pass

    mes_a_num = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
        "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    m_num = mes_a_num.get(mes_encontrado, 7)
    a_num = int(anio_encontrado)
    _, ultimo_dia_mes = calendar.monthrange(a_num, m_num)

    fecha_inicio_str = f"01 / {mes_encontrado} / {anio_encontrado}"
    fecha_fin_str = f"{ultimo_dia_mes:02d} / {mes_encontrado} / {anio_encontrado}"

    lista_productos_ui = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    txt_lista_vacia = ft.Text("Ningún producto seleccionado", size=12, color=c["texto_secundario"], italic=True)

    lista_proveedores_ui = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)

    # --- Lista de proveedores incluidos en el reporte (solo lectura) ---
    def renderizar_lista_proveedores():
        lista_proveedores_ui.controls.clear()
        proveedores_a_mostrar = _proveedores_validos_sin_duplicados(proveedores_seleccionados)
        if proveedores_a_mostrar:
            for prov in proveedores_a_mostrar:
                lista_proveedores_ui.controls.append(
                    ft.Container(
                        bgcolor=c["bg_card_white"],
                        border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        border=ft.BorderSide(1, c["borde_campo"]),
                        content=ft.Row(
                            [
                                ft.Text(prov.get("nombre", ""), size=12, weight=ft.FontWeight.BOLD, color=c["input_bg"], expand=True),
                                ft.Text(prov.get("tipo", ""), size=11, color=c["texto_secundario"]),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )

    renderizar_lista_proveedores()

    # --- Lista de productos incluidos en el reporte (solo lectura) ---
    def renderizar_lista_productos():
        lista_productos_ui.controls.clear()
        if not productos_seleccionados:
            lista_productos_ui.controls.append(txt_lista_vacia)
        else:
            for item in productos_seleccionados:
                prod = item["producto"]
                lista_productos_ui.controls.append(
                    ft.Container(
                        bgcolor=c["bg_card_white"],
                        border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        border=ft.BorderSide(1, c["borde_campo"]),
                        content=ft.Row(
                            [
                                ft.Text(prod.get("nombre", ""), size=12, weight=ft.FontWeight.BOLD, color=c["input_bg"], expand=True),
                                ft.Container(
                                    content=ft.Text(prod.get("tipo", "Producto"), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    bgcolor=c["boton_secundario"],
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    border_radius=12,
                                ),
                                ft.Text(f"{item['piezas']} pz", size=12, color=c["texto_secundario"]),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    )
                )

    renderizar_lista_productos()

    menu_exportar_visible = {"abierto": False}

    # --- Menú de exportación (PDF, Excel, etc.) ---
    def cerrar_menu_exportar():
        menu_exportar_visible["abierto"] = False
        panel_flotante_exportar.visible = False

    def toggle_exportar(e):
        menu_exportar_visible["abierto"] = not menu_exportar_visible["abierto"]
        panel_flotante_exportar.visible = menu_exportar_visible["abierto"]
        page.update()

    def exportar_formato(formato):
        def manejador(e):
            cerrar_menu_exportar()
            snack = ft.SnackBar(
                content=ft.Text(f"Exportando {reporte['nombre']} como {formato}...", color=ft.Colors.WHITE),
                bgcolor="#1565C0",
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        return manejador

    def _boton_formato_exportar(texto, icono):
        return ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Text(texto, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14),
                    ft.Icon(icono, color=ft.Colors.WHITE, size=18),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            style=ft.ButtonStyle(
                side=ft.BorderSide(1.5, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
            width=190,
            height=42,
            on_click=exportar_formato(texto),
        )

    contenido_panel_exportar = ft.Container(
        width=220,
        bgcolor="#5B8DEF",
        border_radius=18,
        padding=16,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1, color="#00000030", offset=ft.Offset(0, 4)),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Exportar reporte", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
                        ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, color=ft.Colors.WHITE, size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                _boton_formato_exportar("Word", ft.Icons.DESCRIPTION_OUTLINED),
                _boton_formato_exportar("PDF", ft.Icons.PICTURE_AS_PDF_OUTLINED),
                _boton_formato_exportar("Excel", ft.Icons.TABLE_CHART_OUTLINED),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    panel_flotante_exportar = ft.Container(content=contenido_panel_exportar, visible=False, top=40, right=0)

    contenido_btn_exportar = ft.Row(
        [
            ft.Text("Exportar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ft.Icon(ft.Icons.DOWNLOAD, color=ft.Colors.WHITE, size=18),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6,
        tight=True,
    )
    btn_exportar = ft.Container(
        content=contenido_btn_exportar,
        bgcolor="#3B82F6",
        border_radius=20,
        height=40,
        padding=ft.Padding.symmetric(horizontal=16, vertical=0),
        alignment=ft.Alignment.CENTER,
        on_click=toggle_exportar,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_exportar,
        ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)),
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        escala_hover=1.05,
    )

    btn_regresar_reporte = ft.Container(
        content=ft.Text("Regresar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor="#3B82F6",
        border_radius=20,
        height=45,
        expand=True,
        margin=ft.Margin.symmetric(horizontal=6),
        alignment=ft.Alignment.CENTER,
        on_click=lambda _: al_regresar_callback(),
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_regresar_reporte,
        ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2)),
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        escala_hover=1.015,
    )

    # --- Valida y guarda los cambios del reporte editado ---
    def accion_guardar_cambios(e):

        reporte["productos_lista"] = productos_seleccionados
        reporte["proveedores_lista"] = _proveedores_validos_sin_duplicados(proveedores_seleccionados)
        reporte["productos"] = temp_productos_count
        reporte["medicamentos"] = temp_medicamentos_count
        reporte["total"] = temp_total_monto

        al_regresar_callback()

        snack = ft.SnackBar(
            content=ft.Text(f"Cambios guardados para '{reporte['nombre']}' exitosamente", color=ft.Colors.WHITE),
            bgcolor="#2E7D32"
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    txt_no_productos = ft.Text(f"No. Productos: {temp_productos_count}", size=13, weight=ft.FontWeight.BOLD, color=c["input_bg"])
    txt_no_medicamentos = ft.Text(f"No. Medicamentos: {temp_medicamentos_count}", size=13, weight=ft.FontWeight.BOLD, color=c["input_bg"])
    txt_total_reporte = ft.Text(f"Total: ${temp_total_monto}", size=13, weight=ft.FontWeight.BOLD, color=c["input_bg"])

    return ft.Container(
        bgcolor=c["fondo_lienzo"],
        border_radius=15,
        padding=20,
        expand=True,
        content=ft.Stack(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(f"Detalles del reporte: {reporte['nombre']}", size=15, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                                ft.Row(
                                    [
                                        txt_no_productos,
                                        txt_no_medicamentos,
                                        txt_total_reporte,
                                        btn_exportar,
                                    ],
                                    spacing=15,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Container(
                            bgcolor=c["fondo_menu"] if modo_oscuro else "#C7D7F9",
                            border_radius=20,
                            padding=20,
                            height=610,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("Rango de fecha del reporte", size=13, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                                            ft.Container(content=ft.Text(fecha_inicio_str, size=12, color=c["input_bg"]), bgcolor=c["bg_card_white"], border_radius=20, border=ft.BorderSide(1, c["borde_campo"]), padding=ft.Padding.symmetric(horizontal=12, vertical=8)),
                                            ft.Text("—", color=c["input_bg"]),
                                            ft.Container(content=ft.Text(fecha_fin_str, size=12, color=c["input_bg"]), bgcolor=c["bg_card_white"], border_radius=20, border=ft.BorderSide(1, c["borde_campo"]), padding=ft.Padding.symmetric(horizontal=12, vertical=8)),
                                        ],
                                        spacing=15,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Container(height=5),
                                    ft.Row(
                                        [

                                            ft.Column(
                                                [
                                                    _encabezado_seccion_dialogo("Lista de proveedores", "#FFFFFF" if modo_oscuro else c["input_bg"]),
                                                    lista_proveedores_ui,
                                                ],
                                                spacing=10,
                                                alignment=ft.MainAxisAlignment.START,
                                                expand=True,
                                            ),
                                            ft.Container(width=20),

                                            ft.Column(
                                                [
                                                    _encabezado_seccion_dialogo("Lista de productos y medicamentos", "#FFFFFF" if modo_oscuro else c["input_bg"]),
                                                    lista_productos_ui,
                                                ],
                                                spacing=10,
                                                alignment=ft.MainAxisAlignment.START,
                                                expand=True,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                        expand=True,
                                    ),
                                    ft.Row(
                                        [
                                            btn_regresar_reporte,
                                        ],
                                        spacing=25,
                                    ),
                                ],
                                spacing=15,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=10,
                    expand=True,
                ),
                panel_flotante_exportar,
            ],
            expand=True,
        ),
    )

# ============================================================
# Diálogo: eliminar reporte (confirmación)
# ============================================================
def _construir_dialogo_eliminar_reporte(page: ft.Page, al_eliminar_callback=None):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]
    reporte_a_borrar_ref = {"reporte": None}

    # --- En modo oscuro usa el mismo estilo que el diálogo de eliminar
    #     producto de inventario.py; en modo claro conserva el estilo original ---
    if modo_oscuro:
        color_fondo_dialogo = c["bg_card_white"]
        color_texto_dialogo = c["input_bg"]
        color_acento_dialogo = c["border"]
    else:
        color_fondo_dialogo = ft.Colors.WHITE
        color_texto_dialogo = c["input_bg"]
        color_acento_dialogo = "#5C88F2"

    def cerrar_dialogo(e=None):
        dialogo.open = False
        page.update()

    texto_advertencia = ft.Text(
        "¿Está segur@ de eliminar el\nreporte?",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=color_texto_dialogo,
        text_align=ft.TextAlign.CENTER,
    )

    # --- Elimina el reporte confirmado ---
    def confirmar_eliminacion(e):
        rep = reporte_a_borrar_ref["reporte"]
        if rep and al_eliminar_callback:
            al_eliminar_callback(rep)
        cerrar_dialogo()

    boton_cancelar = ft.ElevatedButton(
        "Cancelar",
        bgcolor=color_acento_dialogo,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        height=45,
        expand=True,
        on_click=cerrar_dialogo,
    )

    boton_confirmar = ft.ElevatedButton(
        "Eliminar",
        bgcolor="#E53935",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        height=45,
        expand=True,
        on_click=confirmar_eliminacion,
    )

    icono_central = ft.Column(
        [
            ft.Icon(ft.Icons.WARNING_ROUNDED, size=36, color=color_acento_dialogo),
            ft.Icon(ft.Icons.DELETE_OUTLINED, size=28, color=color_acento_dialogo),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    contenido_dialogo = ft.Container(
        width=420,
        padding=25,
        bgcolor=color_fondo_dialogo,
        border_radius=20,
        border=ft.Border.all(2, color_acento_dialogo),
        content=ft.Column(
            [
                texto_advertencia,
                ft.Container(content=icono_central, alignment=ft.Alignment.CENTER, padding=ft.Padding.symmetric(vertical=10)),
                ft.Row(
                    [boton_cancelar, boton_confirmar],
                    spacing=15,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
    )

    dialogo = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor=ft.Colors.TRANSPARENT,
        content=contenido_dialogo,
    )
    page.overlay.append(dialogo)

    def abrir_dialogo(reporte):
        reporte_a_borrar_ref["reporte"] = reporte
        dialogo.open = True
        page.update()

    return dialogo, abrir_dialogo

# ============================================================
# Punto de entrada: vista de Reportes de Ventas (tabla + paginación)
# ============================================================
def vista_reportes(page: ft.Page):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    # --- En modo oscuro, la tarjeta de la lista y los botones (incluida la
    #     paginación) usan el mismo color de sombra que el resto de la UI oscura ---
    if modo_oscuro:
        COLOR_SOMBRA_NORMAL = c["sombra"]
        COLOR_SOMBRA_HOVER = c["sombra"]
    else:
        COLOR_SOMBRA_NORMAL = "#A6B9D8"
        COLOR_SOMBRA_HOVER = "#8FA6D0"

    reportes_ejemplo = _obtener_reportes()
    reportes_filtrados = list(reportes_ejemplo)
    pagina_actual = [1]

    filtro_anio_actual = {"anio": None}
    menu_filtros_visible = {"abierto": False}
    DURACION_ANIM_FILTROS = 260

    anios_disponibles = sorted({r["nombre"].split("_")[-1] for r in reportes_ejemplo}, reverse=True)

    contenedor_principal_vista = ft.Container(expand=True)

    columna_filas = ft.Column(spacing=0)

    fila_numeros_paginacion = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    # --- Controles de paginación ---
    def _ir_pagina_anterior(_):
        pagina_actual[0] -= 1
        actualizar_vista()
        page.update()

    def _ir_pagina_siguiente(_):
        pagina_actual[0] += 1
        actualizar_vista()
        page.update()

    if modo_oscuro:
        SOMBRA_NORMAL_PAG = ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2))
        SOMBRA_HOVER_PAG = ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3))
    else:
        SOMBRA_NORMAL_PAG = ft.BoxShadow(blur_radius=20, spread_radius=1, color=COLOR_SOMBRA_NORMAL, offset=ft.Offset(0, 3))
        SOMBRA_HOVER_PAG = ft.BoxShadow(blur_radius=24, spread_radius=2, color=COLOR_SOMBRA_HOVER, offset=ft.Offset(0, 4))

    icon_btn_izquierda = ft.Container(
        content=ft.Icon(ft.Icons.KEYBOARD_ARROW_LEFT, color=ft.Colors.WHITE if modo_oscuro else c["azul_card"], size=20),
        bgcolor=c["boton_secundario"],
        shape=ft.BoxShape.CIRCLE,
        width=40,
        height=40,
        alignment=ft.Alignment.CENTER,
        on_click=_ir_pagina_anterior,
        ink=True,
    )
    icon_btn_derecha = ft.Container(
        content=ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, color=ft.Colors.WHITE if modo_oscuro else c["azul_card"], size=20),
        bgcolor=c["boton_secundario"],
        shape=ft.BoxShape.CIRCLE,
        width=40,
        height=40,
        alignment=ft.Alignment.CENTER,
        on_click=_ir_pagina_siguiente,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(icon_btn_izquierda, SOMBRA_NORMAL_PAG, SOMBRA_HOVER_PAG)
    _aplicar_hover_boton_paginacion(icon_btn_derecha, SOMBRA_NORMAL_PAG, SOMBRA_HOVER_PAG)

    row_paginacion = ft.Row(
        controls=[
            icon_btn_izquierda,
            ft.Container(
                content=fila_numeros_paginacion,
                width=ANCHO_PAGINADOR_NUMEROS,
                alignment=ft.Alignment.CENTER,
            ),
            icon_btn_derecha,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
    )

    texto_total = ft.Text(
        spans=[
            ft.TextSpan(
                text="Total: ",
                style=ft.TextStyle(color="#0B2B63", weight=ft.FontWeight.BOLD, size=12)
            ),
            ft.TextSpan(
                text="",
                style=ft.TextStyle(color="#1E88E5", weight=ft.FontWeight.BOLD, size=12)
            ),
        ]
    )

    # --- Reconstruye la tabla y el paginador según filtros/página actual ---
    def actualizar_vista():
        total_reportes = len(reportes_filtrados)
        total_paginas = max(1, math.ceil(total_reportes / REPORTES_POR_PAGINA))

        texto_total.spans[1].text = f"{total_reportes} reportes"

        if pagina_actual[0] > total_paginas:
            pagina_actual[0] = total_paginas

        inicio = (pagina_actual[0] - 1) * REPORTES_POR_PAGINA
        fin = inicio + REPORTES_POR_PAGINA
        reportes_pagina = reportes_filtrados[inicio:fin]

        if not reportes_pagina:
            columna_filas.controls = [
                ft.Container(padding=20, content=ft.Text("No se encontraron reportes", color=c["input_bg"], italic=True))
            ]
        else:
            columna_filas.controls = [
                _fila_reporte(
                    r,
                    lambda rep: mostrar_vista_editar(rep),
                    lambda rep: abrir_dialogo_eliminar_reporte(rep),
                    c
                )
                for r in reportes_pagina
            ]

        icon_btn_izquierda.disabled = (pagina_actual[0] == 1)
        icon_btn_izquierda.opacity = 0.4 if icon_btn_izquierda.disabled else 1.0
        icon_btn_derecha.disabled = (pagina_actual[0] == total_paginas)
        icon_btn_derecha.opacity = 0.4 if icon_btn_derecha.disabled else 1.0

        fila_numeros_paginacion.controls.clear()

        for item in _generar_paginas_visibles(pagina_actual[0], total_paginas):
            if item == "...":
                fila_numeros_paginacion.controls.append(
                    ft.Container(
                        content=ft.Text("...", color=c["texto_secundario"], weight=ft.FontWeight.BOLD),
                        padding=ft.Padding.symmetric(horizontal=6, vertical=6),
                    )
                )
                continue

            i = item
            es_activa = i == pagina_actual[0]
            fila_numeros_paginacion.controls.append(
                ft.Container(
                    content=ft.Text(str(i), color=ft.Colors.WHITE if es_activa else c["input_bg"],
                                     weight=ft.FontWeight.BOLD if es_activa else ft.FontWeight.NORMAL),
                    bgcolor=c["azul_card"] if es_activa else None,
                    border_radius=15,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    on_click=lambda _, p=i: [pagina_actual.__setitem__(0, p), actualizar_vista(), page.update()],
                    ink=True,
                )
            )

    # --- Ensamblado de la vista principal: búsqueda + tabla + paginación ---
    def mostrar_vista_principal():
        actualizar_vista()
        panel_flotante_filtros.visible = False
        boton_restaurar.visible = filtro_anio_actual["anio"] is not None
        contenedor_principal_vista.content = ft.Column(
            [
                bar_busqueda,
                header_lista,
                ft.Container(
                    bgcolor=c["bg_card_white"],
                    border_radius=30,
                    padding=10,
                    height=520,
                    shadow=ft.BoxShadow(blur_radius=20, spread_radius=1, color=COLOR_SOMBRA_NORMAL, offset=ft.Offset(0, 3)),
                    content=ft.Column(
                        [_fila_encabezado_tabla(c), ft.Container(content=columna_filas, expand=True)],
                        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
                    ),
                ),
                row_paginacion,
            ],
            spacing=15,
            expand=True,
        )
        page.update()

    # --- Navega a la vista de edición de un reporte ---
    def mostrar_vista_editar(reporte):
        panel_flotante_filtros.visible = False
        boton_restaurar.visible = False
        contenedor_principal_vista.content = _construir_vista_editar_reporte(
            page,
            reporte,
            al_regresar_callback=mostrar_vista_principal
        )
        page.update()

    # --- Aplica búsqueda de texto + filtro por año, y redibuja la tabla ---
    def aplicar_filtros():
        texto_busqueda = (campo_busqueda.value or "").strip().lower()
        reportes_filtrados[:] = [
            r for r in reportes_ejemplo
            if (texto_busqueda in r["nombre"].lower())
            and (filtro_anio_actual["anio"] is None or r["nombre"].split("_")[-1] == filtro_anio_actual["anio"])
        ]
        pagina_actual[0] = 1
        boton_restaurar.visible = filtro_anio_actual["anio"] is not None
        actualizar_vista()
        page.update()

    # --- Filtra reportes por nombre en la barra de búsqueda ---
    def filtrar_reportes(e):
        aplicar_filtros()

    def restaurar_filtros(e):
        filtro_anio_actual["anio"] = None
        aplicar_filtros()

    # --- Elimina el reporte de las listas global y filtrada ---
    def eliminar_reporte_confirmado(rep):
        reportes_ejemplo.remove(rep)
        if rep in reportes_filtrados:
            reportes_filtrados.remove(rep)
        actualizar_vista()
        page.update()

    _, abrir_dialogo_eliminar_reporte = _construir_dialogo_eliminar_reporte(
        page, al_eliminar_callback=eliminar_reporte_confirmado
    )

    # --- Botón flotante para restaurar el filtro por año ---
    boton_restaurar = ft.ElevatedButton(
        "Restaurar filtros", icon=ft.Icons.FILTER_ALT_OFF, bgcolor=c["boton_secundario"],
        color=ft.Colors.WHITE, visible=False, height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=restaurar_filtros
    )

    # --- Panel flotante de filtros: animaciones de apertura/cierre ---
    def _fijar_estado_cerrado_panel():
        panel_flotante_filtros.opacity = 0
        panel_flotante_filtros.scale = ft.Scale(scale=0.85, alignment=ft.Alignment.TOP_CENTER)
        panel_flotante_filtros.offset = ft.Offset(0, -0.08)

    async def _abrir_panel_filtros():
        panel_flotante_filtros.visible = True
        _fijar_estado_cerrado_panel()
        page.update()
        await asyncio.sleep(0.02)
        panel_flotante_filtros.opacity = 1
        panel_flotante_filtros.scale = ft.Scale(scale=1, alignment=ft.Alignment.TOP_CENTER)
        panel_flotante_filtros.offset = ft.Offset(0, 0)
        page.update()

    async def _cerrar_panel_filtros():
        _fijar_estado_cerrado_panel()
        page.update()
        await asyncio.sleep(DURACION_ANIM_FILTROS / 1000)
        panel_flotante_filtros.visible = False
        page.update()

    async def aplicar_filtro_anio(anio):
        filtro_anio_actual["anio"] = anio
        menu_filtros_visible["abierto"] = False
        await _cerrar_panel_filtros()
        aplicar_filtros()

    # --- Botones del panel de filtros por año ---
    def crear_boton_filtro(texto):
        async def _on_click(e, t=texto):
            await aplicar_filtro_anio(t)

        return ft.OutlinedButton(
            texto, width=180, height=35,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                side=ft.BorderSide(1.5, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
            on_click=_on_click
        )

    # --- Tarjeta y contenedor flotante del panel de filtros ---
    contenido_tarjeta_filtros = ft.Container(
        width=230, bgcolor=c["boton_secundario"], border_radius=15, padding=15,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1, color="#A6B9D8", offset=ft.Offset(0, 3)),
        content=ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.FILTER_ALT, color="white", size=18), ft.Text("Filtros", color="white", size=16, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                *[crear_boton_filtro(anio) for anio in anios_disponibles],
            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
        )
    )

    panel_flotante_filtros = ft.Container(
        content=contenido_tarjeta_filtros,
        visible=False,
        top=50,
        right=2,
        opacity=0,
        scale=ft.Scale(scale=0.85, alignment=ft.Alignment.TOP_CENTER),
        offset=ft.Offset(0, -0.08),
        animate_opacity=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
    )

    async def toggle_filtros(e):
        menu_filtros_visible["abierto"] = not menu_filtros_visible["abierto"]
        if menu_filtros_visible["abierto"]:
            await _abrir_panel_filtros()
        else:
            await _cerrar_panel_filtros()

    # --- Barra superior: búsqueda + botón Filtros ---
    campo_busqueda = ft.TextField(
        hint_text="Buscar", prefix_icon=ft.Icons.SEARCH, height=40, border_radius=25, bgcolor=ft.Colors.WHITE,
        content_padding=ft.Padding.only(left=10, right=10), border_color=c["borde_campo"],
        color=c["input_bg"], expand=True, on_change=filtrar_reportes,
    )

    def _crear_boton_pildora(texto, icono, on_click_handler):
        contenido_boton = ft.Row(
            [
                ft.Icon(icono, color=ft.Colors.WHITE, size=18),
                ft.Text(texto, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            tight=True,
        )
        boton = ft.Container(
            content=contenido_boton,
            bgcolor=c["boton_secundario"],
            border_radius=19,
            height=38,
            padding=ft.Padding.symmetric(horizontal=16, vertical=0),
            alignment=ft.Alignment.CENTER,
            on_click=on_click_handler,
            ink=True,
        )
        SOMBRA_NORMAL_PILDORA = ft.BoxShadow(blur_radius=20, spread_radius=1, color=COLOR_SOMBRA_NORMAL, offset=ft.Offset(0, 3))
        SOMBRA_HOVER_PILDORA = ft.BoxShadow(blur_radius=24, spread_radius=2, color=COLOR_SOMBRA_HOVER, offset=ft.Offset(0, 4))
        _aplicar_hover_boton_paginacion(boton, SOMBRA_NORMAL_PILDORA, SOMBRA_HOVER_PILDORA, escala_hover=1.05)
        return boton

    bar_busqueda = ft.Row(
        [
            campo_busqueda,
            _crear_boton_pildora("Filtros", ft.Icons.FILTER_ALT, toggle_filtros),
        ],
        spacing=10,
    )

    # --- Encabezado de la lista (título + total de reportes) ---
    header_lista = ft.Row(
        [ft.Text("Lista de reportes de ventas", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=14), texto_total],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    mostrar_vista_principal()

    return ft.Stack(
        [
            contenedor_principal_vista,
            panel_flotante_filtros,
            ft.Container(content=boton_restaurar, right=20, bottom=20),
        ],
        expand=True,
    )