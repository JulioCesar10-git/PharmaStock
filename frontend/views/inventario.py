import asyncio
import math
import random
import tkinter as tk
from datetime import date
from tkinter import filedialog

import flet as ft

from frontend.theme import colores
from frontend.state import ESTADO_FARMACIA, ESTADO_UI, PRODUCTOS_GLOBALES, obtener_estado_caducidad
from frontend.components.producto_card import crear_tarjeta_producto
from frontend.alertas_inventario import contar_avisos_inventario
from backend.dao.medicamento_dao import MedicamentoDAO
from backend.dao.producto_dao import ProductoDAO
from backend.dao.proveedor_dao import ProveedorDAO
from backend.models.medicamento import Medicamento
from backend.models.producto import Producto

# --- Conexión con la BD: constantes y helpers de traducción dict <-> DAO ---
CAT_ID_MEDICAMENTOS = 1
CAT_ID_PRODUCTOS = 2
VALOR_DEFECTO_TEXTO = "N/A"
FRACCION_DEFECTO = "Fracción tercera"


def _fecha_mmaaaa_a_date(valor_mmaaaa):
    if not valor_mmaaaa or valor_mmaaaa == "N/A":
        return None
    try:
        mes, anio = valor_mmaaaa.split("/")
        if len(anio) != 4:
            return None
        return date(int(anio), int(mes), 1)
    except (ValueError, AttributeError):
        return None


def _date_a_mmaaaa(valor_date):
    if not valor_date:
        return "N/A"
    return f"{valor_date.month:02d}/{valor_date.year}"


def _precio_a_float(valor_precio):
    return float(valor_precio) if valor_precio is not None else 0.0


def _medicamento_a_dict(med):
    return {
        "id": med.med_id,
        "tipo": "Medicamento",
        "categoria": "Medicamento",
        "nombre": med.med_nombreGen,
        "precio": _precio_a_float(med.med_precio),
        "stock": med.med_existencia,
        "caducidad": _date_a_mmaaaa(med.med_fechaCad),
        "alertas": [],
        "lote": med.med_lote,
        "codigo": med.med_codBarras,
        "prov_id": med.prov_id,
        "cat_id": med.cat_id,
        "fraccion": med.med_fraccion,
        "marca": None,
        "imagen": med.med_imagen,
    }


def _producto_a_dict(prod):
    return {
        "id": prod.prod_id,
        "tipo": "Producto",
        "categoria": "Producto",
        "nombre": prod.prod_nombre,
        "precio": _precio_a_float(prod.prod_precio),
        "stock": prod.prod_existencia,
        "caducidad": _date_a_mmaaaa(prod.prod_fechaCad),
        "alertas": [],
        "lote": prod.prod_lote,
        "codigo": prod.prod_codBarras,
        "prov_id": prod.prov_id,
        "cat_id": prod.cat_id,
        "fraccion": prod.prod_fraccion,
        "marca": prod.prod_marca,
        "imagen": prod.prod_imagen,
    }


def _cargar_inventario_bd():
    medicamentos = [_medicamento_a_dict(m) for m in MedicamentoDAO.obtener_todos()]
    productos = [_producto_a_dict(p) for p in ProductoDAO.obtener_todos()]
    return medicamentos + productos


def _crear_producto_bd(datos):
    fecha_cad = _fecha_mmaaaa_a_date(datos.get("caducidad"))

    if datos["tipo"] == "Medicamento":
        med = Medicamento(
            med_codBarras=datos["codigo"],
            med_nombreGen=datos["nombre"],
            med_nombreComer=datos["nombre"],
            med_lab=VALOR_DEFECTO_TEXTO,
            med_origen=VALOR_DEFECTO_TEXTO,
            med_concentracion=VALOR_DEFECTO_TEXTO,
            med_formaFarma=VALOR_DEFECTO_TEXTO,
            med_viaAdmi=VALOR_DEFECTO_TEXTO,
            med_lote=datos["lote"],
            med_fechaCad=fecha_cad,
            med_fraccion=datos.get("fraccion") or FRACCION_DEFECTO,
            med_precio=datos["precio"],
            med_existencia=datos["stock"],
            prov_id=datos["prov_id"],
            cat_id=CAT_ID_MEDICAMENTOS,
            med_imagen=datos.get("imagen"),
        )
        creado = MedicamentoDAO.crear(med)
        return _medicamento_a_dict(creado) if creado else None

    prod = Producto(
        prod_codBarras=datos["codigo"],
        prod_nombre=datos["nombre"],
        prod_marca=datos.get("marca") or VALOR_DEFECTO_TEXTO,
        prod_precio=datos["precio"],
        prod_existencia=datos["stock"],
        prod_lote=datos["lote"],
        prod_fechaCad=fecha_cad,
        prod_fraccion=datos.get("fraccion") or FRACCION_DEFECTO,
        prov_id=datos["prov_id"],
        cat_id=CAT_ID_PRODUCTOS,
        prod_imagen=datos.get("imagen"),
    )
    creado = ProductoDAO.crear(prod)
    return _producto_a_dict(creado) if creado else None


def _actualizar_producto_bd(datos):
    """datos: dict del producto en memoria (con 'id' real) con los valores editados."""
    fecha_cad = _fecha_mmaaaa_a_date(datos.get("caducidad"))

    if datos["tipo"] == "Medicamento":
        med = Medicamento(
            med_id=datos["id"],
            med_codBarras=datos["codigo"],
            med_nombreGen=datos["nombre"],
            med_nombreComer=datos["nombre"],
            med_lab=VALOR_DEFECTO_TEXTO,
            med_origen=VALOR_DEFECTO_TEXTO,
            med_concentracion=VALOR_DEFECTO_TEXTO,
            med_formaFarma=VALOR_DEFECTO_TEXTO,
            med_viaAdmi=VALOR_DEFECTO_TEXTO,
            med_lote=datos["lote"],
            med_fechaCad=fecha_cad,
            med_fraccion=datos.get("fraccion") or FRACCION_DEFECTO,
            med_precio=datos["precio"],
            med_existencia=datos["stock"],
            prov_id=datos["prov_id"],
            cat_id=datos.get("cat_id") or CAT_ID_MEDICAMENTOS,
            med_imagen=datos.get("imagen"),
        )
        return MedicamentoDAO.actualizar(med)

    prod = Producto(
        prod_id=datos["id"],
        prod_codBarras=datos["codigo"],
        prod_nombre=datos["nombre"],
        prod_marca=datos.get("marca") or VALOR_DEFECTO_TEXTO,
        prod_precio=datos["precio"],
        prod_existencia=datos["stock"],
        prod_lote=datos["lote"],
        prod_fechaCad=fecha_cad,
        prod_fraccion=datos.get("fraccion") or FRACCION_DEFECTO,
        prov_id=datos["prov_id"],
        cat_id=datos.get("cat_id") or CAT_ID_PRODUCTOS,
        prod_imagen=datos.get("imagen"),
    )
    return ProductoDAO.actualizar(prod)


def _eliminar_producto_bd(producto):
    """producto: dict en memoria con 'id' y 'tipo'."""
    if producto.get("tipo") == "Medicamento":
        return MedicamentoDAO.eliminar(producto["id"])
    return ProductoDAO.eliminar(producto["id"])


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

# --- Formatea un TextField de fecha como MM/AAAA mientras se escribe ---
def formato_mes_ano(e):
        numeros = ''.join(filter(str.isdigit, e.control.value))
        numeros = numeros[:6]

        if len(numeros) >= 3:
            e.control.value = f"{numeros[:2]}/{numeros[2:]}"
        else:
            e.control.value = numeros

        e.control.update()

def vista_inventario(page: ft.Page, modulo_recordatorios=None, on_inventario_actualizado=None):
    # --- Estado y grid de productos ---
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    # --- En modo oscuro, los campos de los diálogos de producto y los
    #     diálogos de confirmación usan el mismo estilo que los de empleados ---
    if modo_oscuro:
        color_fondo_campo = c["boton_secundario"]
        color_texto_campo = ft.Colors.WHITE
        color_hint_campo = ft.Colors.with_opacity(0.55, ft.Colors.WHITE)
        color_label_campo = c["input_bg"]
        color_acento_dialogo = c["border"]
    else:
        color_fondo_campo = "#E9F5FF"
        color_texto_campo = c.get("borde_campo", "#A0C3FF")
        color_hint_campo = ft.Colors.with_opacity(0.45, c.get("borde_campo", "#A0C3FF"))
        color_label_campo = "#004C95"
        color_acento_dialogo = "#5C88F2"

    PRODUCTOS_POR_PAGINA = 12
    pagina_actual = [1]

    # --- Reemplaza los datos de ejemplo por el inventario real de la BD ---
    PRODUCTOS_GLOBALES[:] = _cargar_inventario_bd()
    proveedores_disponibles = ProveedorDAO.obtener_todos()

    productos_filtrados = list(PRODUCTOS_GLOBALES)

    grid_productos = ft.GridView(
        expand=True,
        runs_count=6,
        child_aspect_ratio=0.90,
        spacing=10,
        run_spacing=10,
    )

    # --- Controles de paginación (flechas y números) ---
    fila_numeros_paginacion = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    def cambiar_pagina(nueva_pag):
        pagina_actual[0] = nueva_pag
        actualizar_vista()
        page.update()

    def _ir_pagina_anterior(_):
        pagina_actual[0] -= 1
        actualizar_vista()
        page.update()

    def _ir_pagina_siguiente(_):
        pagina_actual[0] += 1
        actualizar_vista()
        page.update()

    SOMBRA_NORMAL_PAG = ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000010", offset=ft.Offset(0, 2))
    SOMBRA_HOVER_PAG = ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3))

    icon_btn_izquierda = ft.Container(
        content=ft.Icon(ft.Icons.KEYBOARD_ARROW_LEFT, color=ft.Colors.WHITE if ESTADO_UI["modo_oscuro"] else c["azul_card"]),
        bgcolor=c["boton_secundario"],
        border_radius=20,
        width=40,
        height=40,
        alignment=ft.Alignment.CENTER,
        on_click=_ir_pagina_anterior,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(icon_btn_izquierda, SOMBRA_NORMAL_PAG, SOMBRA_HOVER_PAG)

    icon_btn_derecha = ft.Container(
        content=ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, color=ft.Colors.WHITE if ESTADO_UI["modo_oscuro"] else c["azul_card"]),
        bgcolor=c["boton_secundario"],
        border_radius=20,
        width=40,
        height=40,
        alignment=ft.Alignment.CENTER,
        on_click=_ir_pagina_siguiente,
        ink=True,
    )
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
    texto_resumen_inventario = ft.Text(
        "",
        size=11,
        color=ft.Colors.WHITE if ESTADO_UI["modo_oscuro"] else c["fondo_menu"],
        weight=ft.FontWeight.BOLD,
    )

    # --- Reconstruye el grid de productos y el paginador según filtros/página actual ---
    def actualizar_vista():
        total_general = len(productos_filtrados)
        total_medicamentos = sum(1 for prod in productos_filtrados if prod.get("tipo") == "Medicamento")
        total_otros_productos = total_general - total_medicamentos
        total_paginas = max(1, math.ceil(total_general / PRODUCTOS_POR_PAGINA))

        texto_resumen_inventario.value = f"{total_otros_productos} productos | {total_medicamentos} medicamentos"

        if pagina_actual[0] > total_paginas:
            pagina_actual[0] = total_paginas

        inicio = (pagina_actual[0] - 1) * PRODUCTOS_POR_PAGINA
        fin = inicio + PRODUCTOS_POR_PAGINA
        productos_pagina = productos_filtrados[inicio:fin]

        if not productos_pagina:
            grid_productos.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=48, color=c.get("azul_card", "#5C88F2")),
                            ft.Text(
                                "No se encontraron productos",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=c.get("input_bg", "#183883")
                            ),
                            ft.Text(
                                "Intenta buscar con otro término o revisa la ortografía.",
                                size=16,
                                color=ft.Colors.GREY_500
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                )
            ]

        else:
            grid_productos.controls = [
                crear_tarjeta_producto(
                    producto=prod,
                    on_editar=abrir_dialogo_edit,
                    on_eliminar=abrir_dialogo_eliminar
                )
                for prod in productos_pagina
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
                        content=ft.Text("...", color=c.get("texto_secundario", "#6C7A94"), weight=ft.FontWeight.BOLD),
                        padding=ft.Padding.symmetric(horizontal=6, vertical=6),
                    )
                )
                continue

            i = item
            es_activa = i == pagina_actual[0]
            fila_numeros_paginacion.controls.append(
                ft.Container(
                    content=ft.Text(
                        str(i),
                        color=ft.Colors.WHITE if es_activa else c["input_bg"],
                        weight=ft.FontWeight.BOLD if es_activa else ft.FontWeight.NORMAL,
                    ),
                    bgcolor=c["azul_card"] if es_activa else None,
                    border_radius=15,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    on_click=lambda _, p=i: cambiar_pagina(p),
                    ink=True,
                )
            )

    filtro_actual = {"nombre": None}
    menu_filtros_visible = {"abierto": False}

    DURACION_ANIM_FILTROS = 260

    # --- Panel de filtros: aplicar / restaurar / abrir-cerrar ---
    def aplicar_filtros(e=None):
        texto_busqueda = (campo_busqueda.value or "").strip().lower()

        resultado = PRODUCTOS_GLOBALES
        if texto_busqueda:
            resultado = [p for p in resultado if texto_busqueda in p["nombre"].lower()]

        filtro = filtro_actual["nombre"]
        if filtro == "Medicamentos":
            resultado = [p for p in resultado if p.get("tipo") == "Medicamento"]
        elif filtro == "Productos":
            resultado = [p for p in resultado if p.get("tipo") != "Medicamento"]
        elif filtro == "Por caducar":
            resultado = [p for p in resultado if obtener_estado_caducidad(p.get("caducidad")) == "Por caducar"]
        elif filtro == "Caducados":
            resultado = [p for p in resultado if obtener_estado_caducidad(p.get("caducidad")) == "Caducado"]
        elif filtro == "Stock bajo":
            resultado_filtrado = []
            for p in resultado:

                alertas = p.get("alertas", [])
                tiene_alerta = False
                if isinstance(alertas, list):
                    tiene_alerta = any("stock bajo" in str(alerta).lower() for alerta in alertas)

                stock_raw = p.get("stock", 0)
                if isinstance(stock_raw, str):
                    numeros_str = "".join(filter(str.isdigit, stock_raw))
                    stock_num = int(numeros_str) if numeros_str else 999
                else:
                    stock_num = int(stock_raw) if stock_raw is not None else 999

                if tiene_alerta or stock_num <= 50:
                    resultado_filtrado.append(p)

            resultado = resultado_filtrado

        productos_filtrados[:] = resultado
        pagina_actual[0] = 1
        actualizar_vista()
        page.update()

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

    async def aplicar_filtro_tipo(nombre_filtro):
        filtro_actual["nombre"] = nombre_filtro
        menu_filtros_visible["abierto"] = False
        boton_restaurar.visible = True
        await _cerrar_panel_filtros()
        aplicar_filtros()

    def restaurar_filtros(e):
        filtro_actual["nombre"] = None
        boton_restaurar.visible = False
        aplicar_filtros()

    async def toggle_filtros(e):
        menu_filtros_visible["abierto"] = not menu_filtros_visible["abierto"]
        if menu_filtros_visible["abierto"]:
            await _abrir_panel_filtros()
        else:
            await _cerrar_panel_filtros()

    # --- Botones tipo píldora del panel de filtros ---
    def crear_boton_filtro(texto):
        async def _on_click(e, t=texto):
            await aplicar_filtro_tipo(t)

        return ft.OutlinedButton(
            texto,
            width=180,
            height=35,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                side=ft.BorderSide(1.5, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
            on_click=_on_click,
        )

    contenido_tarjeta_filtros = ft.Container(
        width=230,
        bgcolor=c["boton_secundario"],
        border_radius=15,
        padding=15,
        shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=1,
                color="#A6B9D8",
                offset=ft.Offset(0, 3),
            ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.FILTER_ALT, color="white", size=18),
                        ft.Text("Filtros", color="white", size=16, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
                crear_boton_filtro("Medicamentos"),
                crear_boton_filtro("Productos"),
                crear_boton_filtro("Por caducar"),
                crear_boton_filtro("Caducados"),
                crear_boton_filtro("Stock bajo"),
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
    )

    panel_flotante_filtros = ft.Container(
        content=contenido_tarjeta_filtros,
        visible=False,
        top=70,
        right=20,

        opacity=0,
        scale=ft.Scale(scale=0.85, alignment=ft.Alignment.TOP_CENTER),
        offset=ft.Offset(0, -0.08),
        animate_opacity=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(DURACION_ANIM_FILTROS, ft.AnimationCurve.EASE_OUT),
    )

    boton_restaurar = ft.ElevatedButton(
        "Restaurar filtros",
        icon=ft.Icons.FILTER_ALT_OFF,
        bgcolor=c["boton_secundario"],
        color=ft.Colors.WHITE,
        visible=False,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=restaurar_filtros,
    )

    campo_busqueda = ft.TextField(
        hint_text="Buscar",
        prefix_icon=ft.Icons.SEARCH,
        height=40,
        border_radius=30,
        bgcolor=ft.Colors.WHITE,
        content_padding=ft.Padding.only(left=10, right=10),
        border_color=c.get("borde_campo", "#A0C3FF"),
        color=c.get("input_bg", "#183883"),
        expand=True,
        on_change=aplicar_filtros,
    )

    # --- Helpers para construir campos con etiqueta (formulario agregar) ---
    def _crear_campo(label, widget, expandir=False, label_color=None, label_size=12, error_ctrl=None):
        if label_color is None:
            label_color = c.get("input_bg", "#183883")

        lbl = ft.Text(label, size=label_size, weight=ft.FontWeight.BOLD, color=label_color)
        contenido_columna = [lbl, widget]
        if error_ctrl is not None:
            contenido_columna.append(error_ctrl)
        contenedor = ft.Container(
            content=ft.Column(
                contenido_columna,
                spacing=4,
            ),
            expand=expandir
        )
        contenedor.lbl = lbl
        return contenedor

    def _crear_tf(**kwargs):
        default_args = dict(
            border_color="#A0C3FF",
            border_radius=30,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            text_style=ft.TextStyle(color="#5C88F2"),
            width=float("inf"),
        )
        default_args.update(kwargs)
        return ft.TextField(**default_args)

    def _crear_dd(opciones, val_inicial=None, **kwargs):
        default_args = dict(
            options=[ft.dropdown.Option(opt) for opt in opciones],
            value=val_inicial,
            border_color="#A0C3FF",
            border_radius=30,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            text_style=ft.TextStyle(color="#5C88F2"),
            width=540,
        )
        default_args.update(kwargs)
        return ft.Dropdown(**default_args)

    bloque_imagen = ft.Stack(
        [
            ft.Container(
                width=130, height=130,
                border=ft.Border.all(1.5, "#A0C3FF"), border_radius=12,
                content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color="#A0C3FF", size=48)
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, color="#5C88F2", size=18),
                bgcolor=ft.Colors.WHITE, shape=ft.BoxShape.CIRCLE, padding=8,
                shadow=ft.BoxShadow(blur_radius=4, color="#00000030"),
                bottom=-6, right=-6
            )
        ],
        width=140, height=140
    )

    linea_separadora = ft.Container(
        content=ft.Text("- " * 60, color="#5C88F2", size=14, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.CLIP),
        alignment=ft.Alignment.CENTER
    )

    ESTILO_CAMPO_ADD = dict(
        height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo,
        text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18),
        content_padding=ft.Padding.only(left=15), border_color=c.get("borde_campo", "#A0C3FF"),
        width=float("inf"),
    )
    ESTILO_DROPDOWN_ADD = dict(
        height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo,
        content_padding=ft.Padding.only(left=15), border_color=c.get("borde_campo", "#A0C3FF"),
        color=color_texto_campo, text_size=18, expand=True,
    )

    def _crear_tf_add(**kwargs):
        estilo = dict(ESTILO_CAMPO_ADD)
        estilo.update(kwargs)
        return ft.TextField(**estilo)

    def _crear_dd_add(opciones, val_inicial=None, **kwargs):
        estilo = dict(ESTILO_DROPDOWN_ADD)
        estilo["options"] = [ft.dropdown.Option(opt) for opt in opciones]
        estilo["value"] = val_inicial
        estilo.update(kwargs)
        return ft.Dropdown(**estilo)

    # --- Tooltips informativos para cada fracción de medicamento ---
    TOOLTIPS_FRACCION = {
        "Fracción primera": "Requiere receta especial para su venta",
        "Fracción segunda": "Requiere receta médica ordinaria para su venta",
        "Fracción tercera": "No requiere receta médica para su venta",
    }

    def _opciones_fraccion_con_tooltip():
        return [
            ft.dropdown.Option(key=texto, content=ft.Container(content=ft.Text(texto), tooltip=tip))
            for texto, tip in TOOLTIPS_FRACCION.items()
        ]

    # --- Estado de la imagen seleccionada para el producto nuevo ---
    imagen_add_seleccionada = {"path": None}

    TAMANO_RECUADRO_IMAGEN_ADD = 200  # <-- cambia este número para ajustar el tamaño del recuadro

    def _icono_imagen_vacia():
        return ft.Icon(
            ft.Icons.IMAGE_OUTLINED,
            color=c.get("borde_campo", "#A0C3FF"),
            size=int(TAMANO_RECUADRO_IMAGEN_ADD * 0.4),
        )

    contenedor_preview_imagen_add = ft.Container(
        width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD, bgcolor=c.get("fondo_lienzo", "#EBF3FF"),
        border=ft.Border.all(1.5, c.get("borde_campo", "#A0C3FF")), border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=_icono_imagen_vacia(),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    # --- Selector de imagen vía tkinter.filedialog (independiente de la versión de Flet) ---
    EXTENSIONES_IMAGEN = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]

    def _seleccionar_archivo_imagen():
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            ruta = filedialog.askopenfilename(
                title="Selecciona una imagen del producto",
                filetypes=EXTENSIONES_IMAGEN,
            )
        finally:
            raiz.destroy()
        return ruta

    def _abrir_selector_imagen_add(e):
        ruta = _seleccionar_archivo_imagen()

        if not ruta:
            return

        imagen_add_seleccionada["path"] = ruta

        contenedor_preview_imagen_add.content = ft.Image(
            src=ruta,
            width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD,
            fit=ft.BoxFit.COVER,
            border_radius=12,
        )
        contenedor_preview_imagen_add.update()

    contenedor_click_imagen_add = ft.Container(
        content=contenedor_preview_imagen_add,
        ink=True,
        border_radius=12,
        on_click=_abrir_selector_imagen_add,
        tooltip="Agregar imagen desde tus archivos",
    )
    _aplicar_hover_boton_paginacion(
        contenedor_click_imagen_add,
        ft.BoxShadow(spread_radius=0, blur_radius=0, color="#00000000", offset=ft.Offset(0, 0)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#A9B8CE", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    bloque_imagen_add = ft.Stack(
        [
            contenedor_click_imagen_add,
        ],
        width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD,
        clip_behavior=ft.ClipBehavior.NONE,
    )

    contenedor_bloque_imagen_add = ft.Container(
        content=bloque_imagen_add,
        margin=ft.Margin.only(left=10, top=6, bottom=6),
    )

    linea_separadora_add = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Text("-" * 350, color="#09337F", size=12, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.CLIP),
    )

    def _limpiar_error(err_ctrl):
        if err_ctrl.visible:
            err_ctrl.visible = False
            err_ctrl.update()

    def _crear_texto_error():
        return ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    err_add_nombre = _crear_texto_error()
    err_add_codigo = _crear_texto_error()
    err_add_precio = _crear_texto_error()
    err_add_existencias = _crear_texto_error()
    err_add_caducidad = _crear_texto_error()

    tf_add_nombre = _crear_tf_add(hint_text="Nombre de producto")
    tf_add_nombre.on_change = lambda e: _limpiar_error(err_add_nombre)
    dd_add_tipo = _crear_dd_add(["Medicamento", "Producto"], "Medicamento")
    dd_add_tipo_med = _crear_dd_add(["Analgésico", "Antibiótico", "Antihistamínico", "Otro"], "Analgésico")
    dd_add_fraccion = _crear_dd_add(["Fracción primera", "Fracción segunda", "Fracción tercera"], "Fracción primera", options=_opciones_fraccion_con_tooltip())
    dd_add_marca = _crear_dd_add(["Genérico", "De Patente", "Otra"], "Genérico")
    tf_add_caducidad = _crear_tf_add(hint_text="MM / AAAA", max_length=7, on_change=lambda e: (formato_mes_ano(e), _limpiar_error(err_add_caducidad)), height=65)
    tf_add_lote = _crear_tf_add(read_only=True, bgcolor="#F0F0F0", color=ft.Colors.GREY_500)
    tf_add_codigo = _crear_tf_add(hint_text="7 896 587 54 54", keyboard_type=ft.KeyboardType.NUMBER)
    tf_add_codigo.on_change = lambda e: _limpiar_error(err_add_codigo)
    tf_add_precio = _crear_tf_add(value="$ 150.00", text_align=ft.TextAlign.CENTER)
    tf_add_precio.on_change = lambda e: _limpiar_error(err_add_precio)
    tf_add_existencias = _crear_tf_add(value="100 pz", text_align=ft.TextAlign.CENTER)
    tf_add_existencias.on_change = lambda e: _limpiar_error(err_add_existencias)

    err_add_proveedor = _crear_texto_error()

    def _opciones_proveedor():
        return [ft.dropdown.Option(key=str(p.prov_id), text=p.prov_nombre) for p in proveedores_disponibles]

    dd_add_proveedor = _crear_dd_add([], None)
    dd_add_proveedor.options = _opciones_proveedor()
    dd_add_proveedor.hint_text = "Selecciona un proveedor"
    dd_add_proveedor.on_change = lambda e: _limpiar_error(err_add_proveedor)

    # --- Diálogo "Agregar producto": lógica y campos del formulario ---
    def manejar_cambio_tipo(e):
        es_producto = dd_add_tipo.value == "Producto"
        if es_producto:
            dd_add_tipo_med.disabled = True
            dd_add_tipo_med.value = None
            dd_add_tipo_med.bgcolor = "#F0F0F0"
            dd_add_tipo_med.fill_color = "#F0F0F0"
            dd_add_tipo_med.color = ft.Colors.GREY_500
            dd_add_tipo_med.text_style = ft.TextStyle(color=ft.Colors.GREY_500, size=18)
            dd_add_tipo_med.border_color = ft.Colors.GREY_400
            campo_tipo_med.lbl.color = ft.Colors.GREY_400
            err_add_caducidad.visible = False
        else:
            dd_add_tipo_med.disabled = False
            if not dd_add_tipo_med.value:
                dd_add_tipo_med.value = "Analgésico"
            dd_add_tipo_med.bgcolor = color_fondo_campo
            dd_add_tipo_med.fill_color = color_fondo_campo
            dd_add_tipo_med.color = color_texto_campo
            dd_add_tipo_med.text_style = ft.TextStyle(color=color_texto_campo, size=18)
            dd_add_tipo_med.border_color = c.get("borde_campo", "#A0C3FF")
            campo_tipo_med.lbl.color = color_label_campo

        dd_add_tipo_med.update()
        campo_tipo_med.update()
        contenido_dialogo_add.update()
        page.update()

    dd_add_tipo.on_change = manejar_cambio_tipo

    campo_nombre = _crear_campo("Nombre", tf_add_nombre, label_color=color_label_campo, label_size=18, error_ctrl=err_add_nombre)
    campo_tipo = _crear_campo("Tipo", dd_add_tipo, label_color=color_label_campo, label_size=18)
    campo_tipo_med = _crear_campo("Tipo de medicamento", dd_add_tipo_med, label_color=color_label_campo, label_size=18)
    campo_fraccion = _crear_campo("Fracción de medicamento", dd_add_fraccion, label_color=color_label_campo, label_size=18)
    campo_marca = _crear_campo("Marca de producto", dd_add_marca, label_color=color_label_campo, label_size=18)
    campo_caducidad = _crear_campo("Fecha de caducidad", tf_add_caducidad, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_add_caducidad)
    campo_lote = _crear_campo("Lote", tf_add_lote, expandir=True, label_color=ft.Colors.GREY_400, label_size=18)
    campo_codigo = _crear_campo("Código de barras", tf_add_codigo, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_add_codigo)
    campo_proveedor = _crear_campo("Proveedor", dd_add_proveedor, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_add_proveedor)

    def ajustar_precio(incremento):
        try:
            val_actual = float(tf_add_precio.value.replace("$", "").replace(" ", "").strip())
        except ValueError:
            val_actual = 0.0
        nuevo_val = max(0, val_actual + incremento)
        tf_add_precio.value = f"$ {nuevo_val:.2f}"
        _limpiar_error(err_add_precio)
        page.update()

    def ajustar_existencias(incremento):
        try:
            val_actual = int(tf_add_existencias.value.replace("pz", "").replace(" ", "").strip())
        except ValueError:
            val_actual = 0
        nuevo_val = max(0, val_actual + incremento)
        tf_add_existencias.value = f"{nuevo_val} pz"
        _limpiar_error(err_add_existencias)
        page.update()

    def crear_contador(tf_widget, fn_ajuste, delta):
        btn_menos = ft.Container(
            content=ft.Icon(ft.Icons.REMOVE, color="#5C88F2", size=18),
            bgcolor=ft.Colors.WHITE, shape=ft.BoxShape.CIRCLE, padding=8,
            shadow=ft.BoxShadow(blur_radius=4, color="#00000020"), ink=True,
            on_click=lambda e: fn_ajuste(-delta)
        )
        btn_mas = ft.Container(
            content=ft.Icon(ft.Icons.ADD, color="#5C88F2", size=18),
            bgcolor=ft.Colors.WHITE, shape=ft.BoxShape.CIRCLE, padding=8,
            shadow=ft.BoxShadow(blur_radius=4, color="#00000020"), ink=True,
            on_click=lambda e: fn_ajuste(delta)
        )
        return ft.Row([btn_menos, ft.Container(content=tf_widget, expand=True), btn_mas], spacing=8)

    fila_contadores = ft.Row(
        [
            _crear_campo("Precio", crear_contador(tf_add_precio, ajustar_precio, 5.0), expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_add_precio),
            _crear_campo("Existencias", crear_contador(tf_add_existencias, ajustar_existencias, 1), expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_add_existencias),
        ],
        spacing=20
    )

    btn_atras_add = ft.Container(
        content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
        bgcolor=c.get("boton_secundario", "#89AEEA"), shape=ft.BoxShape.CIRCLE, padding=7,
        margin=ft.Margin.only(left=3, top=3),
        on_click=lambda e: cerrar_dialogo_add(), ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_atras_add,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.05,
    )

    header_add_modal = ft.Row(
        [
            btn_atras_add,
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Añadir producto", size=28, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER),
                        ft.Text("Ingresa los datos:", size=18, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER),
                    ],
                    spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                margin=ft.Margin.only(right=40)
            )
        ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    # --- Valida y guarda el nuevo producto en PRODUCTOS_GLOBALES ---
    def guardar_nuevo_producto(e):
        formulario_valido = True

        if not tf_add_nombre.value or not tf_add_nombre.value.strip():
            err_add_nombre.value = "Es necesario colocar nombre al producto"
            err_add_nombre.visible = True
            formulario_valido = False
        else:
            err_add_nombre.visible = False

        if not tf_add_codigo.value or not tf_add_codigo.value.strip():
            err_add_codigo.value = "Es necesario colocar un código de barras"
            err_add_codigo.visible = True
            formulario_valido = False
        else:
            err_add_codigo.visible = False

        try:
            precio_val = float(tf_add_precio.value.replace("$", "").replace(" ", "").strip())
        except:
            precio_val = 0.0

        if precio_val == 0:
            err_add_precio.value = "El producto tiene que tener un precio"
            err_add_precio.visible = True
            formulario_valido = False
        else:
            err_add_precio.visible = False

        try:
            stock_val = int(tf_add_existencias.value.replace("pz", "").replace(" ", "").strip())
        except:
            stock_val = 0

        if stock_val == 0:
            err_add_existencias.value = "El producto tiene que tener existencias"
            err_add_existencias.visible = True
            formulario_valido = False
        else:
            err_add_existencias.visible = False

        valor_caducidad = tf_add_caducidad.value or ""
        digitos_caducidad = ''.join(filter(str.isdigit, valor_caducidad))

        if not valor_caducidad.strip():
            if dd_add_tipo.value == "Medicamento":
                err_add_caducidad.value = "El medicamento necesita una fecha de caducidad"
                err_add_caducidad.visible = True
                formulario_valido = False
            else:
                err_add_caducidad.visible = False
        elif len(digitos_caducidad) < 6:
            err_add_caducidad.value = "Se requiere llenar todos los campos de la fecha de caducidad"
            err_add_caducidad.visible = True
            formulario_valido = False
        else:
            mes_caducidad = digitos_caducidad[:2]
            anio_caducidad = digitos_caducidad[2:6]
            mes_val = int(mes_caducidad)
            digitos_repetidos = len(set(digitos_caducidad)) == 1

            if digitos_repetidos or mes_val < 1 or mes_val > 12 or anio_caducidad == "0000":
                err_add_caducidad.value = "Se requiere una fecha de caducidad funcional"
                err_add_caducidad.visible = True
                formulario_valido = False
            else:
                err_add_caducidad.visible = False

        if not dd_add_proveedor.value:
            err_add_proveedor.value = "Selecciona un proveedor"
            err_add_proveedor.visible = True
            formulario_valido = False
        else:
            err_add_proveedor.visible = False

        if not formulario_valido:
            contenido_dialogo_add.update()
            return

        datos_nuevo_producto = {
            "nombre": tf_add_nombre.value if tf_add_nombre.value else "Producto Nuevo",
            "tipo": dd_add_tipo.value,
            "precio": precio_val,
            "stock": stock_val,
            "caducidad": tf_add_caducidad.value if tf_add_caducidad.value else "N/A",
            "lote": tf_add_lote.value,
            "codigo": (tf_add_codigo.value or "").strip(),
            "prov_id": int(dd_add_proveedor.value),
            "marca": dd_add_marca.value,
            "fraccion": dd_add_fraccion.value,
            "imagen": imagen_add_seleccionada["path"],
        }

        nuevo_producto = _crear_producto_bd(datos_nuevo_producto)

        if not nuevo_producto:
            snack_error = ft.SnackBar(content=ft.Text("No se pudo guardar el producto en la base de datos", color=ft.Colors.WHITE), bgcolor="#E53935")
            page.overlay.append(snack_error)
            snack_error.open = True
            page.update()
            return

        nuevo_producto["imagen"] = imagen_add_seleccionada["path"]
        nuevo_producto["alertas"] = ["Stock bajo"] if stock_val <= 10 else []

        PRODUCTOS_GLOBALES.insert(0, nuevo_producto)
        aplicar_filtros()
        cerrar_dialogo_add()

        snack = ft.SnackBar(content=ft.Text(f"Producto {nuevo_producto['nombre']} añadido con éxito", color=ft.Colors.WHITE), bgcolor="#2E7D32")
        page.overlay.append(snack)
        snack.open = True
        page.update()

        if isinstance(modulo_recordatorios, dict) and "agregar_aviso" in modulo_recordatorios:
            texto_aviso = f"Nuevo producto en inventario: {nuevo_producto['nombre']} ({nuevo_producto['stock']} pz)"
            modulo_recordatorios["agregar_aviso"](texto_aviso)

        if callable(on_inventario_actualizado):
            on_inventario_actualizado()

    btn_guardar_producto = ft.Container(
        content=ft.Text("Añadir producto", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
        bgcolor=c.get("boton_secundario", "#89AEEA"), border_radius=22,
        padding=ft.Padding.symmetric(vertical=7, horizontal=20),
        margin=ft.Margin.symmetric(horizontal=10, vertical=4),
        alignment=ft.Alignment.CENTER, on_click=guardar_nuevo_producto, ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_guardar_producto,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    contenido_dialogo_add = ft.Container(
        width=820,
        padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        content=ft.Column(
            [
                header_add_modal,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    contenedor_bloque_imagen_add,
                                    ft.Column(
                                        [campo_nombre, campo_tipo, campo_tipo_med],
                                        spacing=14, expand=True
                                    )
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.START, spacing=20
                            ),
                            ft.Container(content=campo_fraccion, expand=True),
                            ft.Container(content=campo_marca, expand=True),
                            ft.Container(content=campo_caducidad, expand=True),
                            ft.Container(content=fila_contadores, expand=True),
                            ft.Row(
                                [
                                    ft.Container(content=campo_lote, expand=True),
                                    ft.Container(content=campo_codigo, expand=True),
                                ],
                                spacing=10
                            ),
                            ft.Container(content=campo_proveedor, expand=True),
                            linea_separadora_add,
                            btn_guardar_producto
                        ],
                        spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.Margin.only(top=35)
                ),
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            tight=True,
        )
    )

    dialogo_add_producto = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor=c.get("bg_card_white", ft.Colors.WHITE),
        shape=ft.RoundedRectangleBorder(radius=26),
        content=contenido_dialogo_add,
    )
    page.overlay.append(dialogo_add_producto)

    # --- Abre/cierra el diálogo de agregar producto ---
    def abrir_dialogo_add(e):
        tf_add_nombre.value = ""
        err_add_nombre.visible = False
        dd_add_tipo.value = "Medicamento"
        dd_add_tipo_med.value = "Analgésico"
        dd_add_fraccion.value = "Fracción primera"
        dd_add_marca.value = "Genérico"
        tf_add_caducidad.value = ""
        err_add_caducidad.visible = False
        tf_add_codigo.value = ""
        err_add_codigo.visible = False
        tf_add_precio.value = "$ 150.00"
        err_add_precio.visible = False
        tf_add_existencias.value = "100 pz"
        err_add_existencias.visible = False
        tf_add_lote.value = f"#{random.randint(1000000, 9999999)}"
        dd_add_proveedor.value = None
        err_add_proveedor.visible = False

        imagen_add_seleccionada["path"] = None
        contenedor_preview_imagen_add.content = _icono_imagen_vacia()

        manejar_cambio_tipo(None)

        dialogo_add_producto.open = True
        page.update()

    def cerrar_dialogo_add():
        dialogo_add_producto.open = False
        page.update()

    producto_a_editar = [None]

    err_edit_nombre = _crear_texto_error()
    err_edit_codigo = _crear_texto_error()
    err_edit_precio = _crear_texto_error()
    err_edit_existencias = _crear_texto_error()
    err_edit_caducidad = _crear_texto_error()

    tf_edit_nombre = _crear_tf_add(hint_text="Nombre de producto")
    tf_edit_nombre.on_change = lambda e: _limpiar_error(err_edit_nombre)
    dd_edit_tipo = _crear_dd_add(["Medicamento", "Producto"], "Medicamento")
    dd_edit_tipo_med = _crear_dd_add(["Analgésico", "Antibiótico", "Antihistamínico", "Otro"], "Analgésico")
    dd_edit_fraccion = _crear_dd_add(["Fracción primera", "Fracción segunda", "Fracción tercera"], "Fracción primera", options=_opciones_fraccion_con_tooltip())
    dd_edit_marca = _crear_dd_add(["Genérico", "De Patente", "Otra"], "Genérico")
    tf_edit_caducidad = _crear_tf_add(hint_text="MM / AAAA", max_length=7, on_change=lambda e: (formato_mes_ano(e), _limpiar_error(err_edit_caducidad)), height=65)
    tf_edit_lote = _crear_tf_add(read_only=True, bgcolor="#F0F0F0", color=ft.Colors.GREY_500)
    tf_edit_codigo = _crear_tf_add(hint_text="7 896 587 54 54", keyboard_type=ft.KeyboardType.NUMBER)
    tf_edit_codigo.on_change = lambda e: _limpiar_error(err_edit_codigo)
    tf_edit_precio = _crear_tf_add(value="$ 150.00", text_align=ft.TextAlign.CENTER)
    tf_edit_precio.on_change = lambda e: _limpiar_error(err_edit_precio)
    tf_edit_existencias = _crear_tf_add(value="100 pz", text_align=ft.TextAlign.CENTER)
    tf_edit_existencias.on_change = lambda e: _limpiar_error(err_edit_existencias)

    err_edit_proveedor = _crear_texto_error()
    dd_edit_proveedor = _crear_dd_add([], None)
    dd_edit_proveedor.options = _opciones_proveedor()
    dd_edit_proveedor.hint_text = "Selecciona un proveedor"
    dd_edit_proveedor.on_change = lambda e: _limpiar_error(err_edit_proveedor)

    def _manejar_cambio_tipo_edit(e):
        es_producto = dd_edit_tipo.value == "Producto"
        if es_producto:
            dd_edit_tipo_med.disabled = True
            dd_edit_tipo_med.value = None
            dd_edit_tipo_med.bgcolor = "#F0F0F0"
            dd_edit_tipo_med.fill_color = "#F0F0F0"
            dd_edit_tipo_med.color = ft.Colors.GREY_500
            dd_edit_tipo_med.text_style = ft.TextStyle(color=ft.Colors.GREY_500, size=18)
            dd_edit_tipo_med.border_color = ft.Colors.GREY_400
            campo_tipo_med_edit.lbl.color = ft.Colors.GREY_400
            _limpiar_error(err_edit_caducidad)
        else:
            dd_edit_tipo_med.disabled = False
            if not dd_edit_tipo_med.value:
                dd_edit_tipo_med.value = "Analgésico"
            dd_edit_tipo_med.bgcolor = color_fondo_campo
            dd_edit_tipo_med.fill_color = color_fondo_campo
            dd_edit_tipo_med.color = color_texto_campo
            dd_edit_tipo_med.text_style = ft.TextStyle(color=color_texto_campo, size=18)
            dd_edit_tipo_med.border_color = c.get("borde_campo", "#A0C3FF")
            campo_tipo_med_edit.lbl.color = color_label_campo

        dd_edit_tipo_med.update()
        campo_tipo_med_edit.update()
        contenido_dialogo_edit.update()
        page.update()

    dd_edit_tipo.on_change = _manejar_cambio_tipo_edit

    # --- Estado de la imagen seleccionada para el producto en edición ---
    imagen_edit_seleccionada = {"path": None}

    contenedor_preview_imagen_edit = ft.Container(
        width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD, bgcolor=c.get("fondo_lienzo", "#EBF3FF"),
        border=ft.Border.all(1.5, c.get("borde_campo", "#A0C3FF")), border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=_icono_imagen_vacia(),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    def _abrir_selector_imagen_edit(e):
        ruta = _seleccionar_archivo_imagen()

        if not ruta:
            return

        imagen_edit_seleccionada["path"] = ruta

        contenedor_preview_imagen_edit.content = ft.Image(
            src=ruta,
            width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD,
            fit=ft.BoxFit.COVER,
            border_radius=12,
        )
        contenedor_preview_imagen_edit.update()

    contenedor_click_imagen_edit = ft.Container(
        content=contenedor_preview_imagen_edit,
        ink=True,
        border_radius=12,
        on_click=_abrir_selector_imagen_edit,
        tooltip="Agregar imagen desde tus archivos",
    )
    _aplicar_hover_boton_paginacion(
        contenedor_click_imagen_edit,
        ft.BoxShadow(spread_radius=0, blur_radius=0, color="#00000000", offset=ft.Offset(0, 0)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#A9B8CE", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    bloque_imagen_edit = ft.Stack(
        [
            contenedor_click_imagen_edit,
        ],
        width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD,
        clip_behavior=ft.ClipBehavior.NONE,
    )

    contenedor_bloque_imagen_edit = ft.Container(
        content=bloque_imagen_edit,
        margin=ft.Margin.only(left=10, top=6, bottom=6),
    )

    # --- Diálogo "Editar producto": ajustes y guardado ---
    def ajustar_precio_edit(incremento):
        try:
            val_actual = float(tf_edit_precio.value.replace("$", "").replace(" ", "").strip())
        except ValueError:
            val_actual = 0.0
        nuevo_val = max(0, val_actual + incremento)
        tf_edit_precio.value = f"$ {nuevo_val:.2f}"
        _limpiar_error(err_edit_precio)
        page.update()

    def ajustar_existencias_edit(incremento):
        try:
            val_actual = int(tf_edit_existencias.value.replace("pz", "").replace(" ", "").strip())
        except ValueError:
            val_actual = 0
        nuevo_val = max(0, val_actual + incremento)
        tf_edit_existencias.value = f"{nuevo_val} pz"
        _limpiar_error(err_edit_existencias)
        page.update()

    def crear_contador_edit(tf_widget, fn_ajuste, delta):
        btn_menos = ft.Container(
            content=ft.Icon(ft.Icons.REMOVE, color="#5C88F2", size=18),
            bgcolor=ft.Colors.WHITE, shape=ft.BoxShape.CIRCLE, padding=8,
            shadow=ft.BoxShadow(blur_radius=4, color="#00000020"), ink=True,
            on_click=lambda e: fn_ajuste(-delta)
        )
        btn_mas = ft.Container(
            content=ft.Icon(ft.Icons.ADD, color="#5C88F2", size=18),
            bgcolor=ft.Colors.WHITE, shape=ft.BoxShape.CIRCLE, padding=8,
            shadow=ft.BoxShadow(blur_radius=4, color="#00000020"), ink=True,
            on_click=lambda e: fn_ajuste(delta)
        )
        return ft.Row([btn_menos, ft.Container(content=tf_widget, expand=True), btn_mas], spacing=8)

    fila_contadores_edit = ft.Row(
        [
            _crear_campo("Precio", crear_contador_edit(tf_edit_precio, ajustar_precio_edit, 5.0), expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_precio),
            _crear_campo("Existencias", crear_contador_edit(tf_edit_existencias, ajustar_existencias_edit, 1), expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_existencias),
        ],
        spacing=20
    )

    btn_atras_edit = ft.Container(
        content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
        bgcolor=c.get("boton_secundario", "#89AEEA"), shape=ft.BoxShape.CIRCLE, padding=7,
        margin=ft.Margin.only(left=3, top=3),
        on_click=lambda e: cerrar_dialogo_edit(), ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_atras_edit,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.05,
    )

    header_edit_modal = ft.Row(
        [
            btn_atras_edit,
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Editar producto", size=28, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER),
                        ft.Text("Cambia los datos del producto", size=18, color=c.get("input_bg", "#183883"), text_align=ft.TextAlign.CENTER),
                    ],
                    spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                margin=ft.Margin.only(right=40)
            )
        ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    # --- Valida y aplica los cambios del producto editado ---
    def guardar_cambios_producto(e):
        if not producto_a_editar[0]:
            return

        formulario_valido = True

        if not tf_edit_nombre.value or not tf_edit_nombre.value.strip():
            err_edit_nombre.value = "Es necesario colocar nombre al producto"
            err_edit_nombre.visible = True
            formulario_valido = False
        else:
            err_edit_nombre.visible = False

        if not tf_edit_codigo.value or not tf_edit_codigo.value.strip():
            err_edit_codigo.value = "Es necesario colocar un código de barras"
            err_edit_codigo.visible = True
            formulario_valido = False
        else:
            err_edit_codigo.visible = False

        try:
            precio_val = float(tf_edit_precio.value.replace("$", "").replace(" ", "").strip())
        except:
            precio_val = 0.0

        if precio_val == 0:
            err_edit_precio.value = "El producto tiene que tener un precio"
            err_edit_precio.visible = True
            formulario_valido = False
        else:
            err_edit_precio.visible = False

        try:
            stock_val = int(tf_edit_existencias.value.replace("pz", "").replace(" ", "").strip())
        except:
            stock_val = 0

        if stock_val == 0:
            err_edit_existencias.value = "El producto tiene que tener existencias"
            err_edit_existencias.visible = True
            formulario_valido = False
        else:
            err_edit_existencias.visible = False

        valor_caducidad = tf_edit_caducidad.value or ""
        digitos_caducidad = ''.join(filter(str.isdigit, valor_caducidad))

        if not valor_caducidad.strip():
            if dd_edit_tipo.value == "Medicamento":
                err_edit_caducidad.value = "El medicamento necesita una fecha de caducidad"
                err_edit_caducidad.visible = True
                formulario_valido = False
            else:
                err_edit_caducidad.visible = False
        elif len(digitos_caducidad) < 6:
            err_edit_caducidad.value = "Se requiere llenar todos los campos de la fecha de caducidad"
            err_edit_caducidad.visible = True
            formulario_valido = False
        else:
            mes_caducidad = digitos_caducidad[:2]
            anio_caducidad = digitos_caducidad[2:6]
            mes_val = int(mes_caducidad)
            digitos_repetidos = len(set(digitos_caducidad)) == 1

            if digitos_repetidos or mes_val < 1 or mes_val > 12 or anio_caducidad == "0000":
                err_edit_caducidad.value = "Se requiere una fecha de caducidad funcional"
                err_edit_caducidad.visible = True
                formulario_valido = False
            else:
                err_edit_caducidad.visible = False

        if not dd_edit_proveedor.value:
            err_edit_proveedor.value = "Selecciona un proveedor"
            err_edit_proveedor.visible = True
            formulario_valido = False
        else:
            err_edit_proveedor.visible = False

        if not formulario_valido:
            contenido_dialogo_edit.update()
            return

        prod = producto_a_editar[0]

        datos_editados = {
            "id": prod.get("id"),
            "tipo": dd_edit_tipo.value,
            "nombre": tf_edit_nombre.value if tf_edit_nombre.value else "Sin nombre",
            "precio": precio_val,
            "stock": stock_val,
            "caducidad": tf_edit_caducidad.value if tf_edit_caducidad.value else "N/A",
            "lote": tf_edit_lote.value,
            "codigo": (tf_edit_codigo.value or "").strip(),
            "prov_id": int(dd_edit_proveedor.value),
            "cat_id": prod.get("cat_id"),
            "marca": dd_edit_marca.value,
            "fraccion": dd_edit_fraccion.value,
            "imagen": imagen_edit_seleccionada["path"],
        }

        datos_editados["tipo"] = prod.get("tipo")

        exito = _actualizar_producto_bd(datos_editados)

        if not exito:
            snack_error = ft.SnackBar(content=ft.Text("No se pudo actualizar el producto en la base de datos", color=ft.Colors.WHITE), bgcolor="#E53935")
            page.overlay.append(snack_error)
            snack_error.open = True
            page.update()
            return

        prod["nombre"] = datos_editados["nombre"]
        prod["precio"] = datos_editados["precio"]
        prod["stock"] = datos_editados["stock"]
        prod["caducidad"] = datos_editados["caducidad"]
        prod["lote"] = datos_editados["lote"]
        prod["codigo"] = datos_editados["codigo"]
        prod["prov_id"] = datos_editados["prov_id"]
        prod["marca"] = datos_editados["marca"]
        prod["fraccion"] = datos_editados["fraccion"]
        prod["imagen"] = imagen_edit_seleccionada["path"]

        aplicar_filtros()
        cerrar_dialogo_edit()

        snack = ft.SnackBar(content=ft.Text(f"Producto {prod['nombre']} actualizado con éxito", color=ft.Colors.WHITE), bgcolor="#2E7D32")
        page.overlay.append(snack)
        snack.open = True
        page.update()

        if callable(on_inventario_actualizado):
            on_inventario_actualizado()

    btn_guardar_cambios = ft.Container(
        content=ft.Text("Guardar cambios", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
        bgcolor=c.get("boton_secundario", "#89AEEA"), border_radius=22,
        padding=ft.Padding.symmetric(vertical=7, horizontal=20),
        margin=ft.Margin.symmetric(horizontal=10, vertical=4),
        alignment=ft.Alignment.CENTER, on_click=guardar_cambios_producto, ink=True,
    )
    _aplicar_hover_boton_paginacion(
        btn_guardar_cambios,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    campo_tipo_med_edit = _crear_campo("Tipo de medicamento", dd_edit_tipo_med, label_color=color_label_campo, label_size=18)
    campo_proveedor_edit = _crear_campo("Proveedor", dd_edit_proveedor, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_proveedor)

    contenido_dialogo_edit = ft.Container(
        width=820,
        padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        content=ft.Column(
            [
                header_edit_modal,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    contenedor_bloque_imagen_edit,
                                    ft.Column(
                                        [
                                            _crear_campo("Nombre", tf_edit_nombre, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_nombre),
                                            _crear_campo("Tipo", dd_edit_tipo, label_color=color_label_campo, label_size=18),
                                            campo_tipo_med_edit
                                        ],
                                        spacing=14, expand=True
                                    )
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.START, spacing=20
                            ),
                            ft.Container(content=_crear_campo("Fracción de producto", dd_edit_fraccion, label_color=color_label_campo, label_size=18), expand=True),
                            ft.Container(content=_crear_campo("Marca de producto", dd_edit_marca, label_color=color_label_campo, label_size=18), expand=True),
                            ft.Container(content=_crear_campo("Fecha de caducidad", tf_edit_caducidad, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_caducidad), expand=True),
                            ft.Container(content=fila_contadores_edit, expand=True),
                            ft.Row(
                                [
                                    ft.Container(content=_crear_campo("Lote", tf_edit_lote, expandir=True, label_color=ft.Colors.GREY_400, label_size=18), expand=True),
                                    ft.Container(content=_crear_campo("Código de barras", tf_edit_codigo, expandir=True, label_color=color_label_campo, label_size=18, error_ctrl=err_edit_codigo), expand=True),
                                ],
                                spacing=10
                            ),
                            ft.Container(content=campo_proveedor_edit, expand=True),
                            linea_separadora_add,
                            btn_guardar_cambios
                        ],
                        spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.Margin.only(top=35)
                ),
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            tight=True,
        )
    )

    dialogo_edit_producto = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor=c.get("bg_card_white", ft.Colors.WHITE),
        shape=ft.RoundedRectangleBorder(radius=26),
        content=contenido_dialogo_edit,
    )
    page.overlay.append(dialogo_edit_producto)

    # --- Abre/cierra el diálogo de edición, precargando los datos del producto ---
    def abrir_dialogo_edit(prod):
        producto_a_editar[0] = prod
        tf_edit_nombre.value = prod.get("nombre", "")
        err_edit_nombre.visible = False
        dd_edit_tipo.value = prod.get("tipo", "Medicamento")
        dd_edit_tipo.disabled = True  # no se puede migrar entre medicamentos/productos al editar
        dd_edit_tipo_med.value = prod.get("categoria", "Analgésico")
        tf_edit_caducidad.value = prod.get("caducidad", "") if prod.get("caducidad") != "N/A" else ""
        err_edit_caducidad.visible = False
        tf_edit_lote.value = prod.get("lote", "#4505050")
        tf_edit_precio.value = f"$ {prod.get('precio', 0.0):.2f}"
        err_edit_precio.visible = False
        tf_edit_existencias.value = f"{prod.get('stock', 0)} pz"
        err_edit_existencias.visible = False
        tf_edit_codigo.value = prod.get("codigo", "")
        err_edit_codigo.visible = False
        dd_edit_fraccion.value = prod.get("fraccion") or "Fracción primera"
        dd_edit_marca.value = prod.get("marca") or "Genérico"
        prov_id_actual = prod.get("prov_id")
        dd_edit_proveedor.value = str(prov_id_actual) if prov_id_actual else None
        err_edit_proveedor.visible = False

        ruta_imagen_actual = prod.get("imagen")
        imagen_edit_seleccionada["path"] = ruta_imagen_actual
        if ruta_imagen_actual:
            contenedor_preview_imagen_edit.content = ft.Image(
                src=ruta_imagen_actual,
                width=TAMANO_RECUADRO_IMAGEN_ADD, height=TAMANO_RECUADRO_IMAGEN_ADD,
                fit=ft.BoxFit.COVER,
                border_radius=12,
            )
        else:
            contenedor_preview_imagen_edit.content = _icono_imagen_vacia()

        _manejar_cambio_tipo_edit(None)

        dialogo_edit_producto.open = True
        page.update()

    def cerrar_dialogo_edit():
        dialogo_edit_producto.open = False
        page.update()

    producto_a_eliminar = [None]

    # --- Diálogo de confirmación para eliminar un producto ---
    def confirmar_eliminacion_producto(e):
        if not producto_a_eliminar[0]:
            return
        prod = producto_a_eliminar[0]

        if not _eliminar_producto_bd(prod):
            snack_error = ft.SnackBar(content=ft.Text("No se pudo eliminar el producto de la base de datos", color=ft.Colors.WHITE), bgcolor="#E53935")
            page.overlay.append(snack_error)
            snack_error.open = True
            page.update()
            cerrar_dialogo_eliminar()
            return

        if prod in PRODUCTOS_GLOBALES:
            PRODUCTOS_GLOBALES.remove(prod)

        aplicar_filtros()
        cerrar_dialogo_eliminar()

        snack = ft.SnackBar(
            content=ft.Text(f"Producto {prod.get('nombre', '')} eliminado con éxito", color=ft.Colors.WHITE),
            bgcolor="#E53935"
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

        if callable(on_inventario_actualizado):
            on_inventario_actualizado()

    def cerrar_dialogo_eliminar():
        dialogo_eliminar_producto.open = False
        page.update()

    def abrir_dialogo_eliminar(prod):
        producto_a_eliminar[0] = prod
        dialogo_eliminar_producto.open = True
        page.update()

    contenido_dialogo_eliminar = ft.Container(
        width=420,
        padding=25,
        bgcolor=c.get("bg_card_white", ft.Colors.WHITE),
        border_radius=20,
        border=ft.Border.all(2, color_acento_dialogo),
        content=ft.Column(
            [
                ft.Text(
                    "¿Está segur@ de eliminar el producto?",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=c.get("input_bg", "#183883"),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.WARNING_ROUNDED, size=36, color=color_acento_dialogo),
                            ft.Icon(ft.Icons.DELETE_OUTLINED, size=28, color=color_acento_dialogo),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.symmetric(vertical=10),
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Cancelar",
                            bgcolor=color_acento_dialogo,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                            height=45,
                            expand=True,
                            on_click=lambda e: cerrar_dialogo_eliminar(),
                        ),
                        ft.ElevatedButton(
                            "Eliminar",
                            bgcolor="#E53935",
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                            height=45,
                            expand=True,
                            on_click=confirmar_eliminacion_producto,
                        ),
                    ],
                    spacing=15,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            tight=True,
        ),
    )

    dialogo_eliminar_producto = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor=ft.Colors.TRANSPARENT,
        content=contenido_dialogo_eliminar,
    )
    page.overlay.append(dialogo_eliminar_producto)

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
            bgcolor=c.get("boton_secundario", "#89AEEA"),
            border_radius=19,
            height=38,
            padding=ft.Padding.symmetric(horizontal=16, vertical=0),
            alignment=ft.Alignment.CENTER,
            on_click=on_click_handler,
            ink=True,
        )
        if ESTADO_UI["modo_oscuro"]:
            SOMBRA_NORMAL_PILDORA = ft.BoxShadow(blur_radius=10, spread_radius=1, color=c["sombra"], offset=ft.Offset(0, 3))
            SOMBRA_HOVER_PILDORA = ft.BoxShadow(blur_radius=14, spread_radius=2, color=c["sombra"], offset=ft.Offset(0, 4))
        else:
            SOMBRA_NORMAL_PILDORA = ft.BoxShadow(blur_radius=20, spread_radius=1, color="#A6B9D8", offset=ft.Offset(0, 3))
            SOMBRA_HOVER_PILDORA = ft.BoxShadow(blur_radius=24, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4))
        _aplicar_hover_boton_paginacion(boton, SOMBRA_NORMAL_PILDORA, SOMBRA_HOVER_PILDORA, escala_hover=1.05)
        return boton

    bar_busqueda = ft.Row(
        [
            campo_busqueda,
            _crear_boton_pildora("Añadir", ft.Icons.ADD, abrir_dialogo_add),
            _crear_boton_pildora("Filtros", ft.Icons.FILTER_ALT, toggle_filtros),
        ],
        spacing=10,
    )

    texto_nombre_farmacia = ft.Text(ESTADO_FARMACIA["nombre"], size=18, weight=ft.FontWeight.BOLD, color=c.get("input_bg", "#183883"))
    tf_nuevo_nombre_farmacia = ft.TextField(label="Nombre de la farmacia", hint_text="Ej. Farmacia San Martín", max_length=30, autofocus=True)

    # --- Diálogo para editar el nombre de la farmacia ---
    def cerrar_dialogo_farmacia(e):
        dialogo_farmacia.open = False
        page.update()

    def guardar_nombre_farmacia(e):
        if tf_nuevo_nombre_farmacia.value and tf_nuevo_nombre_farmacia.value.strip():
            nuevo_val = tf_nuevo_nombre_farmacia.value.strip()
            ESTADO_FARMACIA["nombre"] = nuevo_val
            texto_nombre_farmacia.value = nuevo_val
        cerrar_dialogo_farmacia(e)

    dialogo_farmacia = ft.AlertDialog(
        title=ft.Text("Editar Nombre de la Farmacia"),
        content=tf_nuevo_nombre_farmacia,
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_farmacia),
            ft.ElevatedButton("Guardar", bgcolor=c.get("boton_secundario", "#89AEEA"), color=ft.Colors.WHITE, on_click=guardar_nombre_farmacia),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_farmacia)

    def abrir_dialogo_farmacia(e):
        valor_actual = ESTADO_FARMACIA["nombre"]
        tf_nuevo_nombre_farmacia.value = "" if valor_actual == "Sin nombre asignado" else valor_actual
        dialogo_farmacia.open = True
        page.update()

    texto_sucursal = ft.Text(f"Sucursal: {ESTADO_FARMACIA['sucursal']}", size=11, color="#2997FF")
    tf_nueva_sucursal = ft.TextField(label="Nombre o dirección de la sucursal", hint_text="Ej. Avenida Cuitlahuac 30 A", autofocus=True)

    # --- Diálogo para editar el nombre de la sucursal ---
    def cerrar_dialogo_sucursal(e):
        dialogo_sucursal.open = False
        page.update()

    def guardar_nombre_sucursal(e):
        if tf_nueva_sucursal.value and tf_nueva_sucursal.value.strip():
            nuevo_val = tf_nueva_sucursal.value.strip()
            ESTADO_FARMACIA["sucursal"] = nuevo_val
            texto_sucursal.value = f"Sucursal: {nuevo_val}"
        cerrar_dialogo_sucursal(e)

    dialogo_sucursal = ft.AlertDialog(
        title=ft.Text("Editar Sucursal"),
        content=tf_nueva_sucursal,
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_sucursal),
            ft.ElevatedButton("Guardar", bgcolor=c.get("boton_secundario", "#89AEEA"), color=ft.Colors.WHITE, on_click=guardar_nombre_sucursal),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_sucursal)

    def abrir_dialogo_sucursal(e):
        valor_actual = ESTADO_FARMACIA["sucursal"]
        tf_nueva_sucursal.value = "" if valor_actual == "Sin sucursal asignada" else valor_actual
        dialogo_sucursal.open = True
        page.update()

    # --- Encabezado: nombre de farmacia, resumen de inventario y sucursal ---
    header_farmacia = ft.Row(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.STORE, color=c.get("input_bg", "#183883"), size=24),
                    texto_nombre_farmacia,
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=c.get("#789CCC", "#5C88F2"), tooltip="Editar farmacia", icon_size=18, on_click=abrir_dialogo_farmacia),
                    ft.Container(
                        content=texto_resumen_inventario,
                        bgcolor=c.get("boton_secundario", "#89AEEA"),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        shadow=ft.BoxShadow(
                                blur_radius=10,
                                spread_radius=1,
                                color=c["sombra"] if ESTADO_UI["modo_oscuro"] else "#A9B8CE",
                                offset=ft.Offset(0, 3),
                            ),
                        border_radius=12,
                    ),
                ],
                spacing=4,
            ),
            ft.Row(
                [
                    texto_sucursal,
                    ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=c.get("#6FB7FB", "#6FB7FB"), tooltip="Editar sucursal", icon_size=16, on_click=abrir_dialogo_sucursal),
                ],
                spacing=2,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    actualizar_vista()

    # --- Ensamblado del contenido principal (búsqueda + grid + paginación) ---
    contenido_principal = ft.Container(
        bgcolor=c.get("fondo_lienzo", "#EBF3FF"),
        border_radius=15,
        padding=20,
        expand=True,
        content=ft.Column(
            [
                bar_busqueda,
                header_farmacia,
                ft.Divider(color=c.get("borde_campo", "#A0C3FF"), height=1),
                grid_productos,
                row_paginacion,
            ],
            spacing=15,
            expand=True,
        ),
    )

    # --- Contenedor raíz: contenido principal + panel de filtros flotante ---
    return ft.Container(
        expand=True,
        content=ft.Stack(
            [
                contenido_principal,
                panel_flotante_filtros,
                ft.Container(content=boton_restaurar, right=35, bottom=35),
            ],
            expand=True,
        ),
    )