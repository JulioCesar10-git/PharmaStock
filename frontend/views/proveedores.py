import asyncio
import math
import re
import copy

import flet as ft
import requests

from frontend.theme import colores
from frontend.state import PROVEEDORES_GLOBALES, PRODUCTOS_GLOBALES, ESTADO_UI

from backend.dao.proveedor_dao import ProveedorDAO
from backend.models.proveedor import Proveedor

PROVEEDORES_POR_PAGINA = 7
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
    ("Tipo de proveedor", 2),
    ("Productos", 1),
    ("Contacto", 2),
]
EXPAND_ACCIONES = 1

# --- Consulta colonias a partir de un código postal (API externa) ---
def _obtener_colonias_por_cp(codigo_postal):
    try:
        respuesta = requests.get(
            f"https://postali.app/api/v1/mx/cp/{codigo_postal}",
            timeout=5,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        colonias = sorted({
            asentamiento["nombre"]
            for asentamiento in datos.get("asentamientos", [])
            if asentamiento.get("nombre")
        })
        return colonias
    except Exception:
        return []

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

# --- Fila de encabezado de la tabla de proveedores ---
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
def _fila_proveedor(proveedor, on_editar, on_eliminar, c):
    valores = [f"{proveedor['no']:02d}", proveedor["nombre"], proveedor["tipo"], str(proveedor["productos"]), proveedor["contacto"]]
    colores_texto = [c["input_bg"], c["input_bg"], c["azul_card"], c["input_bg"], c["texto_secundario"]]
    pesos = [ft.FontWeight.NORMAL, ft.FontWeight.BOLD, ft.FontWeight.NORMAL, ft.FontWeight.NORMAL, ft.FontWeight.NORMAL]

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
                        content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=18, color="#1E88E5"),
                        bgcolor=c["bg_card_white"],
                        shape=ft.BoxShape.CIRCLE,
                        padding=9,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color="#C2D1EB", offset=ft.Offset(0, 1)),
                        on_click=lambda e, p=proveedor: on_editar(p),
                        tooltip="Editar",
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE, size=18, color="#E53935"),
                        bgcolor=c["bg_card_white"],
                        shape=ft.BoxShape.CIRCLE,
                        padding=9,
                        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color="#C2D1EB", offset=ft.Offset(0, 1)),
                        on_click=lambda e, p=proveedor: on_eliminar(p),
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

# --- Helpers de UI para la vista de edición ---
def _linea_punteada_seccion(color, size=12):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(-1, 0),
        content=ft.Text(
            "-" * 200,
            color=color,
            size=size,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

def _divisor_seccion(titulo, color):
    return ft.Row(
        controls=[
            _linea_punteada_seccion(color),
            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=color),
            _linea_punteada_seccion(color),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

# ============================================================
# Vista: editar proveedor (datos, ubicación, productos que surte)
# ============================================================
def _construir_vista_editar_proveedor(page: ft.Page, proveedor, al_regresar_callback):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    # --- En modo oscuro, la tarjeta que engloba la información toma el mismo
    #     azul oscuro que la barra de navegación lateral, los textos y las
    #     líneas punteadas se vuelven blancos, y los campos/dropdowns usan
    #     ese mismo azul de fondo para integrarse con la tarjeta ---
    if modo_oscuro:
        color_tarjeta = c["fondo_menu"]
        color_sombra_tarjeta = c["sombra"]
        color_texto_labels = ft.Colors.WHITE
        color_divisor = ft.Colors.WHITE
        color_fondo_campo = c["fondo_menu"]
        color_texto_campo = ft.Colors.WHITE
        color_fondo_contenedor_info = c["fondo_menu"]
        color_texto_contenedor_info = ft.Colors.WHITE
    else:
        color_tarjeta = "#A9C3F7"
        color_sombra_tarjeta = "#A6B9D8"
        color_texto_labels = "#004C95"
        color_divisor = "#09337F"
        color_fondo_campo = "#E9F5FF"
        color_texto_campo = c["borde_campo"]
        color_fondo_contenedor_info = c["bg_card_white"]
        color_texto_contenedor_info = c["input_bg"]

    proveedor.setdefault("correo", "")
    proveedor.setdefault("cp", "")
    proveedor.setdefault("colonia", "")
    proveedor.setdefault("calle", "")
    proveedor.setdefault("numero", "")
    proveedor.setdefault("fraccion", "Fracción primera")
    proveedor.setdefault("productos_lista", [])

    lada_inicial, telefono_inicial = "+52", ""
    coincidencia = re.match(r"\((.*?)\)(.*)", proveedor.get("contacto", "") or "")
    if coincidencia:
        lada_inicial, telefono_inicial = coincidencia.group(1), coincidencia.group(2)

    productos_seleccionados = copy.deepcopy(proveedor.get("productos_lista", []))

    estilo_campo = dict(
        height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo,
        text_size=16, content_padding=ft.Padding.only(left=15),
        border_color=c["borde_campo"],
    )
    estilo_dropdown = dict(
        height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo,
        content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"],
        color=color_texto_campo, text_size=16,
    )

    txt_nombre = ft.TextField(value=proveedor.get("nombre", ""), expand=True, **estilo_campo)
    dd_lada = ft.Dropdown(
        options=[ft.dropdown.Option("+52"), ft.dropdown.Option("+1"), ft.dropdown.Option("+35")],
        value=lada_inicial, **estilo_dropdown,
    )
    txt_telefono = ft.TextField(value=telefono_inicial, expand=True, **estilo_campo)
    txt_correo = ft.TextField(value=proveedor.get("correo", ""), expand=True, **estilo_campo)

    # --- Textos de error (mismas reglas que en el modal "Añadir proveedor") ---
    def _crear_texto_error_proveedor():
        return ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    def _limpiar_error_proveedor(err_ctrl):
        if err_ctrl.visible:
            err_ctrl.visible = False
            err_ctrl.update()

    err_nombre = _crear_texto_error_proveedor()
    err_telefono = _crear_texto_error_proveedor()
    err_correo = _crear_texto_error_proveedor()
    err_cp = _crear_texto_error_proveedor()

    txt_nombre.on_change = lambda e: _limpiar_error_proveedor(err_nombre)
    txt_correo.on_change = lambda e: _limpiar_error_proveedor(err_correo)

    # --- Solo dígitos y máximo 10 caracteres en el teléfono, igual que en Añadir proveedor ---
    def _formatear_telefono_editar(e):
        numeros = ''.join(filter(str.isdigit, txt_telefono.value or ""))[:10]
        txt_telefono.value = numeros
        _limpiar_error_proveedor(err_telefono)
        txt_telefono.update()

    txt_telefono.on_change = _formatear_telefono_editar

    # --- Autocompleta colonia al escribir el código postal ---
    def _cp_cambio_editar(e):
        _limpiar_error_proveedor(err_cp)
        valor = (txt_cp.value or "").strip()
        if len(valor) != 5 or not valor.isdigit():
            return

        colonias = _obtener_colonias_por_cp(valor)
        if colonias:
            dd_colonia.options = [ft.dropdown.Option(colonia) for colonia in colonias]
            dd_colonia.value = colonias[0]
        else:
            dd_colonia.options = [ft.dropdown.Option("No se encontraron resultados para ese C.P.")]
            dd_colonia.value = "No se encontraron resultados para ese C.P."
        page.update()

    txt_cp = ft.TextField(value=proveedor.get("cp", ""), expand=True, on_change=_cp_cambio_editar, **estilo_campo)
    dd_colonia = ft.Dropdown(
        options=[ft.dropdown.Option(proveedor.get("colonia") or "Ingresa un C.P. válido")],
        value=proveedor.get("colonia") or "Ingresa un C.P. válido",
        expand=True, **estilo_dropdown,
    )
    txt_numero = ft.TextField(value=proveedor.get("numero", ""), **estilo_campo)
    txt_calle = ft.TextField(value=proveedor.get("calle", ""), expand=True, **estilo_campo)

    dd_tipo = ft.Dropdown(
        options=[ft.dropdown.Option("Medicamentos"), ft.dropdown.Option("Productos")],
        value=proveedor.get("tipo", "Medicamentos"), expand=True, **estilo_dropdown,
    )
    dd_fraccion = ft.Dropdown(
        options=[
            ft.dropdown.Option("Fracción primera"), ft.dropdown.Option("Fracción segunda"),
            ft.dropdown.Option("Fracción tercera"), ft.dropdown.Option("Fracción cuarta"),
        ],
        value=proveedor.get("fraccion", "Fracción primera"), expand=True, **estilo_dropdown,
    )

    lista_productos_ui = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    txt_lista_vacia = ft.Text("Ningún producto seleccionado", size=12, color=c["texto_secundario"], italic=True)

    def _opciones_productos_disponibles():
        nombres_ya = {p.get("nombre") for p in productos_seleccionados}
        return [ft.dropdown.Option(p.get("nombre", "")) for p in PRODUCTOS_GLOBALES if p.get("nombre") not in nombres_ya]

    # --- Lista editable de productos que surte el proveedor ---
    def _renderizar_lista_productos():
        lista_productos_ui.controls.clear()
        if not productos_seleccionados:
            lista_productos_ui.controls.append(txt_lista_vacia)
        else:
            for i, prod in enumerate(productos_seleccionados):
                lista_productos_ui.controls.append(
                    ft.Container(
                        bgcolor=color_fondo_contenedor_info, border_radius=10,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        border=ft.BorderSide(1, c["borde_campo"]),
                        content=ft.Row(
                            [
                                ft.Text(prod.get("nombre", ""), size=13, weight=ft.FontWeight.BOLD, color=color_texto_contenedor_info, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE, icon_size=14, icon_color=c["text_red"],
                                    tooltip="Quitar producto",
                                    on_click=lambda e, idx=i: _quitar_producto(idx),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )

    def _agregar_producto(e):
        nombre_sel = dd_producto.value
        if not nombre_sel:
            return
        prod = next((p for p in PRODUCTOS_GLOBALES if p.get("nombre") == nombre_sel), {"nombre": nombre_sel})
        if prod not in productos_seleccionados:
            productos_seleccionados.append(prod)
        dd_producto.value = None
        dd_producto.options = _opciones_productos_disponibles()
        _renderizar_lista_productos()
        page.update()

    def _quitar_producto(idx):
        productos_seleccionados.pop(idx)
        dd_producto.options = _opciones_productos_disponibles()
        _renderizar_lista_productos()
        page.update()

    dd_producto = ft.Dropdown(
        hint_text="Seleccionar producto",
        options=_opciones_productos_disponibles(),
        on_select=_agregar_producto,
        expand=True,
        **estilo_dropdown,
    )

    _renderizar_lista_productos()

    # --- Valida (mismas reglas que "Añadir proveedor") y guarda los cambios del proveedor ---
    def accion_guardar_cambios(e):
        formulario_valido = True

        nombre_val = txt_nombre.value.strip() if txt_nombre.value else ""
        if not nombre_val:
            err_nombre.value = "Es necesario insertar nombre de proveedor"
            err_nombre.visible = True
            formulario_valido = False
        elif any(
            p is not proveedor and (p.get("nombre") or "").strip().lower() == nombre_val.lower()
            for p in PROVEEDORES_GLOBALES
        ):
            err_nombre.value = "Ya existe un proveedor con ese nombre"
            err_nombre.visible = True
            formulario_valido = False
        else:
            err_nombre.visible = False

        digitos_telefono = ''.join(filter(str.isdigit, txt_telefono.value or ""))

        if not digitos_telefono:
            err_telefono.value = "Es necesario insertar un número telefónico"
            err_telefono.visible = True
            formulario_valido = False
        elif len(digitos_telefono) < 10:
            err_telefono.value = "Es necesario insertar un numero telefónico funcional"
            err_telefono.visible = True
            formulario_valido = False
        else:
            err_telefono.visible = False

        correo_val = txt_correo.value.strip() if txt_correo.value else ""
        if not correo_val:
            err_correo.value = "Es necesario colocar un correo electrónico"
            err_correo.visible = True
            formulario_valido = False
        elif " " in correo_val:
            err_correo.value = "No se pueden dejar espacios en el correo"
            err_correo.visible = True
            formulario_valido = False
        elif "@" not in correo_val:
            err_correo.value = "Es necesario ingresar un @"
            err_correo.visible = True
            formulario_valido = False
        else:
            err_correo.visible = False

        if not txt_cp.value or not txt_cp.value.strip():
            err_cp.value = "Es necesario insertar un código postal"
            err_cp.visible = True
            formulario_valido = False
        else:
            err_cp.visible = False

        if not formulario_valido:
            page.update()
            return

        proveedor["nombre"] = txt_nombre.value or proveedor.get("nombre", "Sin nombre")
        proveedor["tipo"] = dd_tipo.value or proveedor.get("tipo", "Medicamentos")
        proveedor["correo"] = txt_correo.value or ""
        proveedor["cp"] = txt_cp.value or ""
        _colonia_valida = dd_colonia.value not in (None, "Ingresa un C.P. válido", "No se encontraron resultados para ese C.P.")
        proveedor["colonia"] = dd_colonia.value if _colonia_valida else ""
        proveedor["numero"] = txt_numero.value or ""
        proveedor["calle"] = txt_calle.value or ""
        proveedor["fraccion"] = dd_fraccion.value or proveedor.get("fraccion", "Fracción primera")
        proveedor["contacto"] = f"({dd_lada.value}){txt_telefono.value}"
        proveedor["productos_lista"] = productos_seleccionados

        prov_obj = Proveedor(
        prov_id=proveedor.get("prov_id"),
        prov_nombre=proveedor["nombre"],
        prov_telefono=proveedor["contacto"],
        prov_calle=proveedor["calle"],
        prov_num=proveedor["numero"],
        prov_colonia=proveedor["colonia"],
        prov_municipio="",
        prov_estado="",
        prov_codigoPostal=int(proveedor["cp"]) if proveedor.get("cp", "").isdigit() else 0,
        prov_correo=proveedor["correo"],
        prov_tipo=proveedor["tipo"]
        )
        ProveedorDAO.actualizar(prov_obj)

        proveedor["productos"] = len(productos_seleccionados)

        al_regresar_callback()

        snack = ft.SnackBar(
            content=ft.Text(f"Cambios guardados para '{proveedor['nombre']}' exitosamente", color=ft.Colors.WHITE),
            bgcolor="#2E7D32",
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    _sombra_botones = ft.BoxShadow(
        blur_radius=20,
        spread_radius=1,
        color="#A6B9D8",
        offset=ft.Offset(0, 3),
    )

    boton_regresar = ft.Container(
        content=ft.Text("Regresar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor="#3B82F6",
        border_radius=24,
        height=48,
        expand=True,
        margin=ft.Margin.symmetric(horizontal=4),
        alignment=ft.Alignment.CENTER,
        on_click=lambda _: al_regresar_callback(),
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_regresar,
        _sombra_botones,
        ft.BoxShadow(blur_radius=24, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )
    boton_guardar = ft.Container(
        content=ft.Text("Guardar cambios", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor="#1DD75B",
        border_radius=24,
        height=48,
        expand=True,
        margin=ft.Margin.symmetric(horizontal=4),
        alignment=ft.Alignment.CENTER,
        on_click=accion_guardar_cambios,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_guardar,
        _sombra_botones,
        ft.BoxShadow(blur_radius=24, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    columna_izquierda = ft.Column(
        [
            ft.Text("Nombre", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            txt_nombre,
            err_nombre,
            ft.Text("Número telefónico", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            ft.Row([ft.Container(width=130, content=dd_lada), txt_telefono], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            err_telefono,
            ft.Text("Correo electrónico", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            txt_correo,
            err_correo,
            _divisor_seccion("Dirección", color_divisor),
            ft.Text("Código postal", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            txt_cp,
            err_cp,
            ft.Text("Colonia", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            dd_colonia,
            ft.Row(
                [
                    ft.Column([ft.Text("Número", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels), ft.Container(width=100, content=txt_numero)], spacing=5),
                    ft.Column([ft.Text("Calle", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels), txt_calle], spacing=5, expand=True),
                ],
                spacing=10, vertical_alignment=ft.CrossAxisAlignment.END,
            ),
        ],
        spacing=4, expand=True, tight=True,
    )

    columna_derecha = ft.Column(
        [
            ft.Text("Tipo de proveedor", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            ft.Row([dd_tipo], expand=False),
            ft.Text("Fracción de productos", size=16, weight=ft.FontWeight.BOLD, color=color_texto_labels),
            ft.Row([dd_fraccion], expand=False),
            _divisor_seccion("Lista de productos", color_divisor),
            ft.Row([dd_producto], expand=False),
            ft.Container(
                content=lista_productos_ui,
                expand=True,
                bgcolor=color_fondo_contenedor_info if modo_oscuro else ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                border_radius=10,
                padding=4,
            ),
        ],
        spacing=4, expand=True, tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return ft.Container(
        bgcolor=c["fondo_lienzo"],
        border_radius=15,
        padding=ft.Padding.only(left=20, right=20, top=8, bottom=8),
        expand=True,
        content=ft.Column(
            [
                ft.Text("Editar información del proveedor", size=18, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
                ft.Container(
                    bgcolor=color_tarjeta,
                    border_radius=20,
                    padding=18,
                    expand=True,
                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        spread_radius=1,
                        color=color_sombra_tarjeta,
                        offset=ft.Offset(0, 3),
                    ),
                    content=ft.Column(
                        [
                            ft.Row(
                                [columna_izquierda, columna_derecha],
                                spacing=30, vertical_alignment=ft.CrossAxisAlignment.STRETCH, expand=True,
                            ),
                            ft.Row([boton_regresar, boton_guardar], spacing=25),
                        ],
                        spacing=12, expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
            ],
            spacing=6, expand=True,
        ),
    )

# ============================================================
# Punto de entrada: vista de Proveedores (tabla + paginación + filtros)
# ============================================================
def vista_proveedores(page: ft.Page):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    def _cargar_proveedores():
        proveedores = ProveedorDAO.obtener_todos()
        return [
            {
                "no": i + 1,
                "prov_id": p.prov_id,
                "nombre": p.prov_nombre,
                "tipo": p.prov_tipo,
                "productos": 0,
                "contacto": p.prov_telefono,
                "correo": p.prov_correo,
                "cp": str(p.prov_codigoPostal),
                "colonia": p.prov_colonia,
                "calle": p.prov_calle,
                "numero": p.prov_num,
            }
            for i, p in enumerate(proveedores)
        ]
    proveedores_ejemplo = _cargar_proveedores()

    # --- En modo oscuro, la tarjeta de la lista y los botones (incluida la
    #     paginación) usan el mismo color de sombra que el resto de la UI oscura ---
    if modo_oscuro:
        COLOR_SOMBRA_NORMAL = c["sombra"]
        COLOR_SOMBRA_HOVER = c["sombra"]
    else:
        COLOR_SOMBRA_NORMAL = "#A6B9D8"
        COLOR_SOMBRA_HOVER = "#8FA6D0"

    # --- En modo oscuro, los campos del modal "Añadir proveedor" usan el
    #     mismo estilo que el diálogo de añadir empleado ---
    if modo_oscuro:
        color_fondo_campo = c["boton_secundario"]
        color_texto_campo = ft.Colors.WHITE
        color_hint_campo = ft.Colors.with_opacity(0.55, ft.Colors.WHITE)
        color_label_campo = c["input_bg"]
    else:
        color_fondo_campo = "#E9F5FF"
        color_texto_campo = c["borde_campo"]
        color_hint_campo = ft.Colors.with_opacity(0.45, c["borde_campo"])
        color_label_campo = "#004C95"

    proveedores_filtrados = list(proveedores_ejemplo)
    pagina_actual = [1]
    filtro_tipo_actual = {"tipo": None}
    menu_filtros_visible = {"abierto": False}

    DURACION_ANIM_FILTROS = 260

    contenedor_principal_vista = ft.Container(expand=True)

    columna_filas = ft.Column(spacing=0)
    fila_numeros_paginacion = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)

    # --- Controles de paginación ---
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
            ft.TextSpan(text="Total: ", style=ft.TextStyle(color="#0B2B63", weight=ft.FontWeight.BOLD, size=12)),
            ft.TextSpan(text="", style=ft.TextStyle(color="#1E88E5", weight=ft.FontWeight.BOLD, size=12)),
        ]
    )

    # --- Navega a la vista de edición de un proveedor ---
    def on_editar(proveedor):
        mostrar_vista_editar(proveedor)

    # --- Elimina un proveedor de la lista global ---
    def on_eliminar(proveedor):
        # --- En modo oscuro usa el mismo estilo que el diálogo de eliminar
        #     reporte/producto; en modo claro conserva el estilo original ---
        if modo_oscuro:
            color_fondo_dialogo = c["bg_card_white"]
            color_texto_dialogo = c["input_bg"]
            color_acento_dialogo = c["border"]
        else:
            color_fondo_dialogo = ft.Colors.WHITE
            color_texto_dialogo = "#0B2B63"
            color_acento_dialogo = "#3B82F6"

        def _cancelar_eliminar(e):
            modal_eliminar.open = False
            page.update()

        def _confirmar_eliminar(e):
            ProveedorDAO.eliminar(proveedor["prov_id"])
            proveedores_ejemplo[:] = _cargar_proveedores()
            proveedores_filtrados[:] = list(proveedores_ejemplo)

            modal_eliminar.open = False
            actualizar_vista()

            snack = ft.SnackBar(
                content=ft.Text(f"Proveedor '{proveedor['nombre']}' eliminado correctamente", color=ft.Colors.WHITE),
                bgcolor="#2E7D32",
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

        modal_eliminar = ft.AlertDialog(
            modal=True,
            bgcolor=color_fondo_dialogo,
            shape=ft.RoundedRectangleBorder(radius=26, side=ft.BorderSide(2.5, color_acento_dialogo)),
            content=ft.Container(
                width=500,
                padding=ft.Padding.only(left=15, right=15, top=10, bottom=6),
                content=ft.Column(
                    [
                        ft.Text(
                            "¿Está segur@ de eliminar al proveedor?",
                            size=20, weight=ft.FontWeight.BOLD, color=color_texto_dialogo,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=14),
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.LOCAL_SHIPPING_OUTLINED, size=46, color=color_acento_dialogo),
                                ft.Icon(ft.Icons.DELETE_OUTLINE, size=38, color=color_acento_dialogo),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=40),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Cancelar", color=ft.Colors.WHITE, bgcolor=color_acento_dialogo, expand=True, height=48,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
                                    on_click=_cancelar_eliminar,
                                ),
                                ft.ElevatedButton(
                                    "Eliminar", color=ft.Colors.WHITE, bgcolor="#E53935", expand=True, height=48,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
                                    on_click=_confirmar_eliminar,
                                ),
                            ],
                            spacing=20,
                        ),
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
            ),
        )

        page.overlay.append(modal_eliminar)
        modal_eliminar.open = True
        page.update()

    # --- Reconstruye la tabla y el paginador según filtros/página actual ---
    def actualizar_vista():
        total_proveedores = len(proveedores_filtrados)
        total_paginas = max(1, math.ceil(total_proveedores / PROVEEDORES_POR_PAGINA))
        texto_total.spans[1].text = f"{total_proveedores} proveedores"

        if pagina_actual[0] > total_paginas:
            pagina_actual[0] = total_paginas

        inicio = (pagina_actual[0] - 1) * PROVEEDORES_POR_PAGINA
        fin = inicio + PROVEEDORES_POR_PAGINA
        proveedores_pagina = proveedores_filtrados[inicio:fin]

        if not proveedores_pagina:
            columna_filas.controls = [
                ft.Container(padding=20, content=ft.Text("No se encontraron proveedores", color=c["input_bg"], italic=True))
            ]
        else:
            columna_filas.controls = [_fila_proveedor(p, on_editar, on_eliminar, c) for p in proveedores_pagina]

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
                    on_click=lambda _, p=i: cambiar_pagina(p),
                    ink=True,
                )
            )

        boton_restaurar.visible = filtro_tipo_actual["tipo"] is not None

    # --- Panel de filtros: aplicar / restaurar / abrir-cerrar ---
    def aplicar_filtros(e=None):
        texto_busqueda = (campo_busqueda.value or "").strip().lower()
        tipo_actual = filtro_tipo_actual["tipo"]

        proveedores_filtrados[:] = [
            p for p in proveedores_ejemplo
            if (texto_busqueda == "" or texto_busqueda in p["nombre"].lower() or texto_busqueda in p["tipo"].lower())
            and (tipo_actual is None or p["tipo"] == tipo_actual)
        ]
        pagina_actual[0] = 1
        actualizar_vista()
        page.update()

    def restaurar_filtros(e):
        filtro_tipo_actual["tipo"] = None
        aplicar_filtros()

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

    async def aplicar_filtro_tipo(tipo):
        filtro_tipo_actual["tipo"] = tipo
        menu_filtros_visible["abierto"] = False
        await _cerrar_panel_filtros()
        aplicar_filtros()

    async def toggle_filtros(e):
        menu_filtros_visible["abierto"] = not menu_filtros_visible["abierto"]
        if menu_filtros_visible["abierto"]:
            await _abrir_panel_filtros()
        else:
            await _cerrar_panel_filtros()

    # --- Botones tipo píldora del panel de filtros ---
    def crear_boton_filtro(texto, tipo_valor):
        async def _on_click(e, t=tipo_valor):
            await aplicar_filtro_tipo(t)

        return ft.OutlinedButton(
            texto, width=220, height=35,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                side=ft.BorderSide(1.5, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=20),
            ),
            on_click=_on_click
        )

    contenido_tarjeta_filtros = ft.Container(
        width=270, bgcolor=c["boton_secundario"], border_radius=15, padding=15,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1, color="#A6B9D8", offset=ft.Offset(0, 3)),
        content=ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.FILTER_ALT, color="white", size=18), ft.Text("Filtros", color="white", size=16, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                crear_boton_filtro("Por medicamentos", "Medicamentos"),
                crear_boton_filtro("Por productos", "Productos"),
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

    boton_restaurar = ft.ElevatedButton(
        "Restaurar filtros", icon=ft.Icons.FILTER_ALT_OFF, bgcolor=c["boton_secundario"],
        color=ft.Colors.WHITE, visible=False, height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=restaurar_filtros
    )

    # --- Controles de error para el modal "Agregar proveedor" ---
    def _limpiar_error_proveedor(err_ctrl):
        if err_ctrl.visible:
            err_ctrl.visible = False
            err_ctrl.update()

    def _crear_texto_error_proveedor():
        return ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    err_nombre = _crear_texto_error_proveedor()
    err_telefono = _crear_texto_error_proveedor()

    txt_nombre = ft.TextField(hint_text="Nombre de proveedor", height=45, width=630, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"])
    txt_nombre.on_change = lambda e: _limpiar_error_proveedor(err_nombre)
    dd_lada = ft.Dropdown(options=[ft.dropdown.Option("+52"), ft.dropdown.Option("+1"), ft.dropdown.Option("+35")], value="+52", height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo, content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"], color=color_texto_campo, text_size=18)
    txt_telefono = ft.TextField(hint_text="241-569-5694", height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), expand=True, border_color=c["borde_campo"], keyboard_type=ft.KeyboardType.NUMBER)

    # --- Permite solo dígitos y limita el teléfono a 10 caracteres mientras se escribe ---
    def _formatear_telefono(e):
        numeros = ''.join(filter(str.isdigit, txt_telefono.value or ""))[:10]
        txt_telefono.value = numeros
        _limpiar_error_proveedor(err_telefono)
        txt_telefono.update()

    txt_telefono.on_change = _formatear_telefono
    err_correo = _crear_texto_error_proveedor()
    err_cp = _crear_texto_error_proveedor()

    dd_tipo = ft.Dropdown(options=[ft.dropdown.Option("Medicamentos"), ft.dropdown.Option("Productos")], value="Medicamentos", height=45, width=630, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo, content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"], color=color_texto_campo, text_size=18)
    txt_correo = ft.TextField(hint_text="ejemplo@gmail.com", height=45, width=630, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"], keyboard_type=ft.KeyboardType.EMAIL)
    txt_correo.on_change = lambda e: _limpiar_error_proveedor(err_correo)
    # --- Modal "Agregar proveedor": autocompleta colonia por código postal ---
    def _cp_cambio(e):
        _limpiar_error_proveedor(err_cp)
        valor = (txt_cp.value or "").strip()
        if len(valor) != 5 or not valor.isdigit():
            return

        colonias = _obtener_colonias_por_cp(valor)
        if colonias:
            dd_colonia.options = [ft.dropdown.Option(colonia) for colonia in colonias]
            dd_colonia.value = colonias[0]
        else:
            dd_colonia.options = [ft.dropdown.Option("No se encontraron resultados para ese C.P.")]
            dd_colonia.value = "No se encontraron resultados para ese C.P."
        page.update()

    txt_cp = ft.TextField(hint_text="90100", height=45, width=630, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"], on_change=_cp_cambio)
    txt_numero = ft.TextField(hint_text="30", height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"], keyboard_type=ft.KeyboardType.NUMBER)
    dd_colonia = ft.Dropdown(options=[ft.dropdown.Option("Ingresa un C.P. válido")], value="Ingresa un C.P. válido", height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo, content_padding=ft.Padding.only(left=15), expand=True, border_color=c["borde_campo"], color=color_texto_campo, text_size=18)
    txt_calle = ft.TextField(hint_text="Nombre de la calle", height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo, text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18), content_padding=ft.Padding.only(left=15), expand=True, border_color=c["borde_campo"])

    def cerrar_modal(e):
        modal.open = False
        page.update()

    # --- Valida y agrega el nuevo proveedor a la lista global ---
    def guardar_nuevo_proveedor(e):
        formulario_valido = True

        nombre_val = txt_nombre.value.strip() if txt_nombre.value else ""
        if not nombre_val:
            err_nombre.value = "Es necesario insertar nombre de proveedor"
            err_nombre.visible = True
            formulario_valido = False
        elif any((p.get("nombre") or "").strip().lower() == nombre_val.lower() for p in proveedores_ejemplo):
            err_nombre.value = "Ya existe un proveedor con ese nombre"
            err_nombre.visible = True
            formulario_valido = False
        else:
            err_nombre.visible = False

        digitos_telefono = ''.join(filter(str.isdigit, txt_telefono.value or ""))

        if not digitos_telefono:
            err_telefono.value = "Es necesario insertar un número telefónico"
            err_telefono.visible = True
            formulario_valido = False
        elif len(digitos_telefono) < 10:
            err_telefono.value = "Es necesario insertar un numero telefónico funcional"
            err_telefono.visible = True
            formulario_valido = False
        else:
            err_telefono.visible = False

        correo_val = txt_correo.value.strip() if txt_correo.value else ""
        if not correo_val:
            err_correo.value = "Es necesario colocar un correo electrónico"
            err_correo.visible = True
            formulario_valido = False
        elif " " in correo_val:
            err_correo.value = "No se pueden dejar espacios en el correo"
            err_correo.visible = True
            formulario_valido = False
        elif "@" not in correo_val:
            err_correo.value = "Es necesario ingresar un @"
            err_correo.visible = True
            formulario_valido = False
        else:
            err_correo.visible = False

        if not txt_cp.value or not txt_cp.value.strip():
            err_cp.value = "Es necesario insertar un código postal"
            err_cp.visible = True
            formulario_valido = False
        else:
            err_cp.visible = False

        if not formulario_valido:
            modal.update()
            return

        colonia_valida = dd_colonia.value not in (None, "Ingresa un C.P. válido", "No se encontraron resultados para ese C.P.")

        nuevo_prov = Proveedor(
        prov_nombre=txt_nombre.value or "Sin nombre",
        prov_telefono=f"({dd_lada.value}){txt_telefono.value}",
        prov_calle=txt_calle.value or "",
        prov_num=txt_numero.value or "",
        prov_colonia=dd_colonia.value if colonia_valida else "",
        prov_municipio="",
        prov_estado="",
        prov_codigoPostal=int(txt_cp.value) if txt_cp.value and txt_cp.value.isdigit() else 0,
        prov_correo=txt_correo.value or "",
        prov_tipo=dd_tipo.value or "Medicamentos"
        )
        ProveedorDAO.crear(nuevo_prov)
        proveedores_ejemplo[:] = _cargar_proveedores()
        proveedores_filtrados[:] = list(proveedores_ejemplo)
        pagina_actual[0] = 1

        txt_nombre.value = ""
        txt_telefono.value = ""
        txt_correo.value = ""
        txt_cp.value = ""
        txt_calle.value = ""
        txt_numero.value = ""
        dd_colonia.options = [ft.dropdown.Option("Ingresa un C.P. válido")]
        dd_colonia.value = "Ingresa un C.P. válido"

        modal.open = False

        actualizar_vista()

        snack = ft.SnackBar(content=ft.Text(f"Proveedor {nuevo_prov.prov_nombre} añadido con éxito", color=ft.Colors.WHITE), bgcolor="#2E7D32")
        page.overlay.append(snack)
        snack.open = True

        page.update()

    boton_guardar = ft.Container(
        content=ft.Text("Añadir proveedor", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
        bgcolor=c["boton_secundario"],
        border_radius=22,
        padding=ft.Padding.symmetric(vertical=7, horizontal=20),
        margin=ft.Margin.symmetric(horizontal=10, vertical=4),
        alignment=ft.Alignment.CENTER,
        on_click=guardar_nuevo_proveedor,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_guardar,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    boton_regresar = ft.Container(
        content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
        bgcolor=c["boton_secundario"],
        shape=ft.BoxShape.CIRCLE,
        padding=7,
        margin=ft.Margin.only(left=3, top=3),
        on_click=cerrar_modal,
        ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_regresar,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.05,
    )

    modal = ft.AlertDialog(
        modal=True,
        bgcolor=c["bg_card_white"],
        shape=ft.RoundedRectangleBorder(radius=26),
        content=ft.Container(
            width=650,
            height=610,
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            border_radius=26,
            content=ft.Column(
                [

                    ft.Column(
                        [
                            ft.Stack(
                                [
                                    ft.Row(
                                        [boton_regresar],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Añadir proveedor", size=28, weight=ft.FontWeight.BOLD, color=c["input_bg"])
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                ],
                            ),
                            ft.Row([ft.Text("Ingresa los datos:", size=18, color=c["input_bg"])], alignment=ft.MainAxisAlignment.CENTER),
                        ],
                        spacing=2,
                    ),
                    ft.Container(height=20),

                    ft.Text("Nombre", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    txt_nombre,
                    err_nombre,

                    ft.Text("Número telefónico", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    ft.Row([ft.Container(width=110, content=dd_lada), txt_telefono], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    err_telefono,

                    ft.Text("Tipo de proveedor", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    dd_tipo,

                    ft.Text("Correo electrónico", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    txt_correo,
                    err_correo,

                    ft.Row(
                        [
                            ft.Text("-" * 33, color="#09337F", weight=ft.FontWeight.BOLD),
                            ft.Text("Dirección", size=18, weight=ft.FontWeight.BOLD, color="#09337F"),
                            ft.Text("-" * 33, color="#09337F", weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),

                    ft.Text("Código postal", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    txt_cp,
                    err_cp,

                    ft.Text("Colonia", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
                    dd_colonia,

                    ft.Row([
                        ft.Column([ft.Text("Número", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), ft.Container(width=110, content=txt_numero)], spacing=5),
                        ft.Column([ft.Text("Calle", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), txt_calle], spacing=5, expand=True)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.END),

                    ft.Container(height=8),
                    ft.Row(
                        [ft.Text("-" * 120, color="#09337F", weight=ft.FontWeight.BOLD)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=8),

                    boton_guardar
                ],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            ),
        ),
    )

    # --- Abre el modal de agregar proveedor, limpiando los campos ---
    def abrir_modal(e):
        if modal not in page.overlay:
            page.overlay.append(modal)
        modal.open = True
        page.update()

    campo_busqueda = ft.TextField(
        hint_text="Buscar", prefix_icon=ft.Icons.SEARCH, height=40, border_radius=20, bgcolor=ft.Colors.WHITE,
        content_padding=ft.Padding.only(left=10, right=10), border_color=c["borde_campo"],
        color=c["input_bg"], expand=True, on_change=aplicar_filtros,
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
            _crear_boton_pildora("Añadir", ft.Icons.ADD, abrir_modal),
            _crear_boton_pildora("Filtros", ft.Icons.FILTER_ALT, toggle_filtros),
        ],
        spacing=10,
    )

    # --- Encabezado de la lista (título + total de proveedores) ---
    header_lista = ft.Row(
        [ft.Text("Lista de proveedores", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=14), texto_total],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # --- Tabla de proveedores con botón flotante de restaurar filtros ---
    tabla_con_boton_flotante = ft.Stack(
        [
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
            ft.Container(content=boton_restaurar, right=20, bottom=20),
        ],
    )

    # --- Ensamblado final: alterna entre la vista principal y la de edición ---
    def mostrar_vista_principal():
        actualizar_vista()
        contenedor_principal_vista.content = ft.Stack(
            [
                ft.Column(
                    [
                        bar_busqueda,
                        header_lista,
                        tabla_con_boton_flotante,
                        row_paginacion,
                    ],
                    spacing=15,
                    expand=True,
                ),
                panel_flotante_filtros,
            ],
            expand=True,
        )
        page.update()

    def mostrar_vista_editar(proveedor):
        contenedor_principal_vista.content = _construir_vista_editar_proveedor(
            page, proveedor, al_regresar_callback=mostrar_vista_principal,
        )
        page.update()

    mostrar_vista_principal()

    return contenedor_principal_vista