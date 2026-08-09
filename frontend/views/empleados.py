import asyncio
import tkinter as tk
from tkinter import filedialog

import flet as ft

from frontend.theme import colores
from frontend.state import ESTADO_UI
from frontend.components.empleado_card import crear_tarjeta_empleado

# AGREGAR BACKEND
from backend.dao.usuario_dao import UsuarioDAO
from backend.models.usuario import Usuario

# --- Aplica el mismo efecto hover (zoom + sombra más marcada) que el
#     botón "Agregar tarea" de recordatorios.py, a un Container-botón ---
def _aplicar_hover_boton_paginacion(boton, sombra_normal, sombra_hover, escala_hover=1.05):
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

PUESTOS_DISPONIBLES = [
    "Administrador",
    "Cajero",
    "Almacenista",
]

CODIGOS_PAIS = [
    ("🇲🇽 +52", "+52"),
    ("🇺🇸 +1", "+1"),
    ("🇪🇸 +34", "+34"),
    ("🇨🇴 +57", "+57"),
    ("🇦🇷 +54", "+54"),
    ("🇵🇪 +51", "+51"),
    ("🇨🇱 +56", "+56"),
]

#NUEVO AGREGADO
MAPA_ROL_NIVEL = {
    "admin": "Administradorr",
    "tendero": "Cajeros",
    "bodeguero": "Almacenistas",
}

def _cargar_niveles():
    usuarios = UsuarioDAO.obtener_todos()
    niveles = {
        "Administradorr": [],
        "Cajeros": [],
        "Almacenistas": [],
    }
    for u in usuarios:
        nivel = MAPA_ROL_NIVEL.get(u.usuario_cargo, "Cajeros")
        nombre = f"{u.usuario_usuario} {u.usuario_apellidoPat or ''} {u.usuario_apellidoMat or ''}".strip()
        niveles[nivel].append({
            "usuario_id": u.usuario_id,
            "nombre": nombre,
            "puesto": nivel[:-1] if nivel != "Almacenistas" else "Almacenista",
            "telefono": u.usuario_telefono or "",
            "correo": u.usuario_correoElec,
            "imagen": u.usuario_imagen,
        })
    return [
        {"titulo": "Administradores", "empleados": niveles["Administradorr"]},
        {"titulo": "Cajeros", "empleados": niveles["Cajeros"]},
        {"titulo": "Almacenistas", "empleados": niveles["Almacenistas"]},
    ]

NIVELES_EJEMPLO = _cargar_niveles()

ALTO_FILA_EMPLEADOS = 170


# --- Limita el TextField de teléfono a solo dígitos, máximo 10 ---
def _formato_telefono(e):
    digitos = ''.join(filter(str.isdigit, e.control.value))[:10]
    e.control.value = digitos
    e.control.update()

# --- Helpers de UI reutilizables ---
def _linea_punteada(color, caracter="·", size=16):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(-1, 0),
        content=ft.Text(
            caracter * 350,
            color=color,
            size=size,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

def _encabezado_nivel(titulo, cantidad, color, c):
    return ft.Row(
        controls=[
            ft.Text(f"{titulo} ({cantidad})", weight=ft.FontWeight.BOLD, color=c["input_bg"], size=13),
            _linea_punteada(color),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

def _campo_con_label(label, hint_text, c, **kwargs_textfield):
    tf = ft.TextField(
        hint_text=hint_text,
        border_color=c["borde_campo"],
        border_radius=30,
        color=c["input_bg"],
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        width=400,
        **kwargs_textfield,
    )
    col = ft.Column(
        [
            ft.Text(label, size=12, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            tf,
        ],
        spacing=4,
    )
    col.tf = tf
    return col

# ============================================================
# Diálogo: agregar empleado
# ============================================================
def _construir_dialogo_agregar_usuario(page: ft.Page, al_guardar_callback=None):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    # --- En modo oscuro, los campos usan el mismo azul que el botón principal ---
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

    estilo_campo = dict(
        height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo,
        text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18),
        content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"],
    )
    estilo_dropdown = dict(
        height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo,
        content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"],
        color=color_texto_campo, text_size=18,
    )

    def _crear_texto_error():
        return ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    def _limpiar_error(err_ctrl):
        if err_ctrl.visible:
            err_ctrl.visible = False
            err_ctrl.update()

    def _campo_agregar(label, hint_text, error_ctrl=None, **kwargs_textfield):
        tf = ft.TextField(hint_text=hint_text, expand=True, **estilo_campo, **kwargs_textfield)
        if error_ctrl is not None:
            tf.on_change = lambda e: _limpiar_error(error_ctrl)
        contenido_columna = [ft.Text(label, size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), tf]
        if error_ctrl is not None:
            contenido_columna.append(error_ctrl)
        col = ft.Column(
            contenido_columna,
            spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, expand=True,
        )
        col.tf = tf
        return col

    # --- Selector de imagen vía tkinter.filedialog ---
    EXTENSIONES_IMAGEN = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]

    def _seleccionar_archivo_imagen():
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            ruta = filedialog.askopenfilename(
                title="Selecciona una foto del empleado",
                filetypes=EXTENSIONES_IMAGEN,
            )
        finally:
            raiz.destroy()
        return ruta

    # --- Estado de la imagen seleccionada para el nuevo empleado ---
    imagen_empleado_seleccionada = {"path": None}

    TAMANO_RECUADRO_IMAGEN = 160

    def _icono_imagen_vacia():
        return ft.Icon(ft.Icons.IMAGE_OUTLINED, color=c["borde_campo"], size=int(TAMANO_RECUADRO_IMAGEN * 0.4))

    recuadro_imagen = ft.Container(
        width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN, bgcolor=c["fondo_lienzo"],
        border=ft.Border.all(1.5, c["borde_campo"]), border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=_icono_imagen_vacia(),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    def _abrir_selector_imagen(e):
        ruta = _seleccionar_archivo_imagen()

        if not ruta:
            return

        imagen_empleado_seleccionada["path"] = ruta

        recuadro_imagen.content = ft.Image(
            src=ruta, width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN, fit=ft.BoxFit.COVER, border_radius=12,
        )
        recuadro_imagen.update()

    recuadro_imagen.ink = True
    recuadro_imagen.on_click = _abrir_selector_imagen
    recuadro_imagen.tooltip = "Agregar imagen desde tus archivos"
    _aplicar_hover_boton_paginacion(
        recuadro_imagen,
        ft.BoxShadow(spread_radius=0, blur_radius=0, color="#00000000", offset=ft.Offset(0, 0)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#A9B8CE", offset=ft.Offset(0, 4)),
        escala_hover=1.03,
    )

    stack_imagen = ft.Stack(
        [recuadro_imagen],
        width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN,
        clip_behavior=ft.ClipBehavior.NONE,
    )

    bloque_imagen = ft.Container(content=stack_imagen, margin=ft.Margin.only(left=6, top=6, bottom=6))

    err_nombre = _crear_texto_error()
    err_apellidos = _crear_texto_error()
    err_telefono = _crear_texto_error()
    err_correo = _crear_texto_error()
    err_contrasena = _crear_texto_error()

    campo_nombre = _campo_agregar("Nombre", "Ingresa nombre", error_ctrl=err_nombre)
    campo_apellidos = _campo_agregar("Apellidos", "Ingresa apellidos", error_ctrl=err_apellidos)

    dropdown_puesto = ft.Dropdown(
        options=[ft.DropdownOption(key=p, text=p) for p in PUESTOS_DISPONIBLES],
        value=PUESTOS_DISPONIBLES[0], expand=True, **estilo_dropdown,
    )
    bloque_puesto = ft.Column(
        [ft.Text("Puesto", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), dropdown_puesto],
        spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    dropdown_codigo_pais = ft.Dropdown(
        value="+52", width=150, **estilo_dropdown,
        options=[ft.DropdownOption(key=codigo, text=etiqueta) for etiqueta, codigo in CODIGOS_PAIS],
    )
    campo_telefono = ft.TextField(
        hint_text="241 569 5694", keyboard_type=ft.KeyboardType.PHONE, expand=True, max_length=10, counter="", **estilo_campo,
    )
    campo_telefono.on_change = lambda e: (_formato_telefono(e), _limpiar_error(err_telefono))
    bloque_telefono = ft.Column(
        [
            ft.Text("Número telefónico", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
            ft.Row([dropdown_codigo_pais, campo_telefono], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            err_telefono,
        ],
        spacing=4,
    )

    campo_correo = _campo_agregar("Correo electrónico", "ejemplo@gmail.com", keyboard_type=ft.KeyboardType.EMAIL, error_ctrl=err_correo)
    campo_contrasena = _campo_agregar("Crear contraseña", "Ingresa +8 caracteres", password=True, can_reveal_password=True, error_ctrl=err_contrasena)

    # --- Cierre del diálogo ---
    def cerrar_dialogo(e=None):
        dialogo.open = False
        page.update()

    boton_regresar = ft.Container(
        content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
        bgcolor=c["boton_secundario"], shape=ft.BoxShape.CIRCLE, padding=7,
        margin=ft.Margin.only(left=3, top=3),
        on_click=cerrar_dialogo, ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_regresar,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.05,
    )

    encabezado = ft.Row(
        [
            boton_regresar,
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Añadir empleado", size=28, weight=ft.FontWeight.BOLD, color=c["input_bg"], text_align=ft.TextAlign.CENTER),
                        ft.Text("Ingresa los datos:", size=18, color=c["input_bg"], text_align=ft.TextAlign.CENTER),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(right=40)
            )
        ], vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # --- Valida y agrega el nuevo empleado al nivel correspondiente ---
    def guardar_usuario(e):
        formulario_valido = True

        nombre_val = campo_nombre.tf.value.strip() if campo_nombre.tf.value else ""
        if not nombre_val:
            err_nombre.value = "Es necesario colocar un nombre"
            err_nombre.visible = True
            formulario_valido = False
        else:
            err_nombre.visible = False

        apellidos_val = campo_apellidos.tf.value.strip() if campo_apellidos.tf.value else ""
        if not apellidos_val:
            err_apellidos.value = "Es necesario colocar un apellido"
            err_apellidos.visible = True
            formulario_valido = False
        else:
            err_apellidos.visible = False

        telefono_val = campo_telefono.value.strip() if campo_telefono.value else ""
        digitos_telefono = ''.join(filter(str.isdigit, telefono_val))
        if not telefono_val:
            err_telefono.value = "Es necesario colocar un número telefónico"
            err_telefono.visible = True
            formulario_valido = False
        elif len(digitos_telefono) != 10:
            err_telefono.value = "Es necesario colocar un número telefónico funcional"
            err_telefono.visible = True
            formulario_valido = False
        else:
            err_telefono.visible = False

        correo_val = campo_correo.tf.value.strip() if campo_correo.tf.value else ""
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

        contrasena_val = campo_contrasena.tf.value.strip() if campo_contrasena.tf.value else ""
        if not contrasena_val:
            err_contrasena.value = "Es necesario colocar una contraseña"
            err_contrasena.visible = True
            formulario_valido = False
        else:
            err_contrasena.visible = False

        if not formulario_valido:
            contenido_dialogo.update()
            return

        nombre_completo = f"{nombre_val} {apellidos_val}"
        puesto_val = dropdown_puesto.value

        MAPA_PUESTO_ROL = {
        "Administrador": "admin",
        "Cajero": "tendero",
        "Almacenista": "bodeguero",
        }

        rol = MAPA_PUESTO_ROL.get(puesto_val, "tendero")
        apellidos_partes = apellidos_val.split(" ", 1)
        apellido_pat = apellidos_partes[0] if len(apellidos_partes) > 0 else ""
        apellido_mat = apellidos_partes[1] if len(apellidos_partes) > 1 else ""

        UsuarioDAO.registrar(
            usuario_usuario=nombre_val,
            usuario_correoElec=correo_val,
            usuario_password=contrasena_val,
            usuario_cargo=rol,
            usuario_apellidoPat=apellido_pat,
            usuario_apellidoMat=apellido_mat,
            usuario_telefono=f"({dropdown_codigo_pais.value}){digitos_telefono}",
            usuario_imagen=imagen_empleado_seleccionada["path"]
        )
        NIVELES_EJEMPLO[:] = _cargar_niveles()

        if al_guardar_callback:
            al_guardar_callback()

        snack = ft.SnackBar(content=ft.Text(f"Empleado '{nombre_completo}' añadido", color=ft.Colors.WHITE), bgcolor="#2E7D32")
        page.overlay.append(snack)
        snack.open = True
        cerrar_dialogo(e)

    boton_guardar = ft.Container(
        content=ft.Text("Añadir empleado", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=18),
        bgcolor=c["boton_secundario"], border_radius=30, padding=10,
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        alignment=ft.Alignment.CENTER, on_click=guardar_usuario, ink=True,
    )

    contenido_dialogo = ft.Container(
        width=820, height=670, padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        content=ft.Column(
            [
                encabezado,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [bloque_imagen, ft.Column([campo_nombre, campo_apellidos, bloque_puesto], spacing=14, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)],
                                spacing=20, vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            bloque_telefono,
                            ft.Row([ft.Container(content=campo_correo, expand=True), ft.Container(content=campo_contrasena, expand=True)], spacing=20),
                            _linea_punteada("#09337F", caracter="-", size=12),
                            boton_guardar,
                        ], spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ), margin=ft.Margin.only(top=35)
                ),
            ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, tight=True,
        ),
    )

    dialogo = ft.AlertDialog(modal=True, bgcolor=c["bg_card_white"], shape=ft.RoundedRectangleBorder(radius=26), content_padding=0, content=contenido_dialogo)
    page.overlay.append(dialogo)

    # --- Abre el diálogo de agregar, limpiando los campos ---
    def abrir_dialogo(e):
        campo_nombre.tf.value = ""
        campo_apellidos.tf.value = ""
        campo_telefono.value = ""
        campo_correo.tf.value = ""
        campo_contrasena.tf.value = ""

        err_nombre.visible = False
        err_apellidos.visible = False
        err_telefono.visible = False
        err_correo.visible = False
        err_contrasena.visible = False

        imagen_empleado_seleccionada["path"] = None
        recuadro_imagen.content = _icono_imagen_vacia()

        dialogo.open = True
        page.update()

    return dialogo, abrir_dialogo

# ============================================================
# Diálogo: editar empleado
# ============================================================
def _construir_dialogo_editar_usuario(page: ft.Page, al_guardar_callback=None):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]

    # --- En modo oscuro, los campos usan el mismo azul que el botón principal ---
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

    estilo_campo = dict(
        height=45, border_radius=30, bgcolor=color_fondo_campo, color=color_texto_campo,
        text_size=18, hint_style=ft.TextStyle(color=color_hint_campo, size=18),
        content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"],
    )
    estilo_dropdown = dict(
        height=45, border_radius=30, filled=True, bgcolor=color_fondo_campo, fill_color=color_fondo_campo,
        content_padding=ft.Padding.only(left=15), border_color=c["borde_campo"],
        color=color_texto_campo, text_size=18,
    )

    def _crear_texto_error():
        return ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    def _limpiar_error(err_ctrl):
        if err_ctrl.visible:
            err_ctrl.visible = False
            err_ctrl.update()

    def _campo_editar(label, hint_text, error_ctrl=None, **kwargs_textfield):
        tf = ft.TextField(hint_text=hint_text, expand=True, **estilo_campo, **kwargs_textfield)
        if error_ctrl is not None:
            tf.on_change = lambda e: _limpiar_error(error_ctrl)
        contenido_columna = [ft.Text(label, size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), tf]
        if error_ctrl is not None:
            contenido_columna.append(error_ctrl)
        col = ft.Column(
            contenido_columna,
            spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH, expand=True,
        )
        col.tf = tf
        return col

    # --- Selector de imagen vía tkinter.filedialog ---
    EXTENSIONES_IMAGEN = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]

    def _seleccionar_archivo_imagen():
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            ruta = filedialog.askopenfilename(
                title="Selecciona una foto del empleado",
                filetypes=EXTENSIONES_IMAGEN,
            )
        finally:
            raiz.destroy()
        return ruta

    # --- Estado de la imagen seleccionada para el empleado en edición ---
    imagen_empleado_seleccionada = {"path": None}

    TAMANO_RECUADRO_IMAGEN = 160

    def _icono_imagen_vacia():
        return ft.Icon(ft.Icons.IMAGE_OUTLINED, color=c["borde_campo"], size=int(TAMANO_RECUADRO_IMAGEN * 0.4))

    recuadro_imagen = ft.Container(
        width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN, bgcolor=c["fondo_lienzo"],
        border=ft.Border.all(1.5, c["borde_campo"]), border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=_icono_imagen_vacia(),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    def _abrir_selector_imagen(e):
        ruta = _seleccionar_archivo_imagen()

        if not ruta:
            return

        imagen_empleado_seleccionada["path"] = ruta

        recuadro_imagen.content = ft.Image(
            src=ruta, width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN, fit=ft.BoxFit.COVER, border_radius=12,
        )
        recuadro_imagen.update()

    recuadro_imagen.ink = True
    recuadro_imagen.on_click = _abrir_selector_imagen
    recuadro_imagen.tooltip = "Agregar imagen desde tus archivos"
    _aplicar_hover_boton_paginacion(
        recuadro_imagen,
        ft.BoxShadow(spread_radius=0, blur_radius=0, color="#00000000", offset=ft.Offset(0, 0)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#A9B8CE", offset=ft.Offset(0, 4)),
        escala_hover=1.03,
    )

    stack_imagen = ft.Stack(
        [recuadro_imagen],
        width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN,
        clip_behavior=ft.ClipBehavior.NONE,
    )

    bloque_imagen = ft.Container(content=stack_imagen, margin=ft.Margin.only(left=6, top=6, bottom=6))

    err_nombre = _crear_texto_error()
    err_apellidos = _crear_texto_error()
    err_telefono = _crear_texto_error()
    err_correo = _crear_texto_error()
    err_contrasena = _crear_texto_error()

    campo_nombre = _campo_editar("Nombre", "Ingresa nombre", error_ctrl=err_nombre)
    campo_apellidos = _campo_editar("Apellidos", "Ingresa apellidos", error_ctrl=err_apellidos)

    dropdown_puesto = ft.Dropdown(
        options=[ft.DropdownOption(key=p, text=p) for p in PUESTOS_DISPONIBLES],
        value=PUESTOS_DISPONIBLES[0], expand=True, **estilo_dropdown,
    )
    bloque_puesto = ft.Column(
        [ft.Text("Puesto", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo), dropdown_puesto],
        spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    dropdown_codigo_pais = ft.Dropdown(
        value="+52", width=150, **estilo_dropdown,
        options=[ft.DropdownOption(key=codigo, text=etiqueta) for etiqueta, codigo in CODIGOS_PAIS],
    )
    campo_telefono = ft.TextField(
        hint_text="241 569 5694", keyboard_type=ft.KeyboardType.PHONE, expand=True, max_length=10, counter="", **estilo_campo,
    )
    campo_telefono.on_change = lambda e: (_formato_telefono(e), _limpiar_error(err_telefono))
    bloque_telefono = ft.Column(
        [
            ft.Text("Número telefónico", size=18, weight=ft.FontWeight.BOLD, color=color_label_campo),
            ft.Row([dropdown_codigo_pais, campo_telefono], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            err_telefono,
        ],
        spacing=4,
    )

    campo_correo = _campo_editar("Correo electrónico", "ejemplo@gmail.com", keyboard_type=ft.KeyboardType.EMAIL, error_ctrl=err_correo)
    campo_contrasena = _campo_editar("Nueva contraseña (opcional)", "Dejar en blanco para mantener", password=True, can_reveal_password=True, error_ctrl=err_contrasena)

    empleado_actual_ref = {"empleado": None}

    def cerrar_dialogo(e=None):
        dialogo.open = False
        page.update()

    boton_regresar = ft.Container(
        content=ft.Icon(ft.Icons.REPLY, color=ft.Colors.WHITE, size=16),
        bgcolor=c["boton_secundario"], shape=ft.BoxShape.CIRCLE, padding=7,
        margin=ft.Margin.only(left=3, top=3),
        on_click=cerrar_dialogo, ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_regresar,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.05,
    )

    encabezado = ft.Row(
        [
            boton_regresar,
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        ft.Text("Editar empleado", size=28, weight=ft.FontWeight.BOLD, color=c["input_bg"], text_align=ft.TextAlign.CENTER),
                        ft.Text("Modifica los datos:", size=18, color=c["input_bg"], text_align=ft.TextAlign.CENTER),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                margin=ft.Margin.only(right=40)
            )
        ], vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # --- Valida y aplica los cambios del empleado editado ---
    def guardar_cambios(e):
        emp = empleado_actual_ref["empleado"]
        if not emp:
            return

        formulario_valido = True

        nombre_val = campo_nombre.tf.value.strip() if campo_nombre.tf.value else ""
        if not nombre_val:
            err_nombre.value = "Es necesario colocar un nombre"
            err_nombre.visible = True
            formulario_valido = False
        else:
            err_nombre.visible = False

        apellidos_val = campo_apellidos.tf.value.strip() if campo_apellidos.tf.value else ""
        if not apellidos_val:
            err_apellidos.value = "Es necesario colocar un apellido"
            err_apellidos.visible = True
            formulario_valido = False
        else:
            err_apellidos.visible = False

        telefono_val = campo_telefono.value.strip() if campo_telefono.value else ""
        digitos_telefono = ''.join(filter(str.isdigit, telefono_val))
        if not telefono_val:
            err_telefono.value = "Es necesario colocar un número telefónico"
            err_telefono.visible = True
            formulario_valido = False
        elif len(digitos_telefono) != 10:
            err_telefono.value = "Es necesario colocar un número telefónico funcional"
            err_telefono.visible = True
            formulario_valido = False
        else:
            err_telefono.visible = False

        correo_val = campo_correo.tf.value.strip() if campo_correo.tf.value else ""
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

        contrasena_val = campo_contrasena.tf.value.strip() if campo_contrasena.tf.value else ""
        if contrasena_val and len(contrasena_val) <= 8:
            err_contrasena.value = "La contraseña debe tener más de 8 caracteres"
            err_contrasena.visible = True
            formulario_valido = False
        else:
            err_contrasena.visible = False

        if not formulario_valido:
            contenido_dialogo.update()
            return

        emp["nombre"] = f"{nombre_val} {apellidos_val}".strip()
        nuevo_puesto = dropdown_puesto.value

        if emp["puesto"] != nuevo_puesto:
            antiguo_nivel_titulo = MAPA_ROL_NIVEL.get(emp["puesto"], "Almacenistas")
            nuevo_nivel_titulo = MAPA_ROL_NIVEL.get(nuevo_puesto, "Almacenistas")

            for nivel in NIVELES_EJEMPLO:
                if nivel["titulo"] == antiguo_nivel_titulo and emp in nivel["empleados"]:
                    nivel["empleados"].remove(emp)
                    break

            emp["puesto"] = nuevo_puesto
            for nivel in NIVELES_EJEMPLO:
                if nivel["titulo"] == nuevo_nivel_titulo:
                    nivel["empleados"].append(emp)
                    break

        emp["telefono"] = digitos_telefono
        emp["correo"] = correo_val
        emp["imagen"] = imagen_empleado_seleccionada["path"]

        if al_guardar_callback:
            al_guardar_callback()

        snack = ft.SnackBar(content=ft.Text(f"Cambios guardados para '{emp['nombre']}'", color=ft.Colors.WHITE), bgcolor="#1976D2")
        page.overlay.append(snack)
        snack.open = True
        cerrar_dialogo(e)

    boton_guardar = ft.Container(
        content=ft.Text("Guardar cambios", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=16),
        bgcolor=c["boton_secundario"], border_radius=22, padding=ft.Padding.symmetric(vertical=7, horizontal=20),
        margin=ft.Margin.symmetric(horizontal=10, vertical=4),
        alignment=ft.Alignment.CENTER, on_click=guardar_cambios, ink=True,
    )
    _aplicar_hover_boton_paginacion(
        boton_guardar,
        ft.BoxShadow(blur_radius=10, spread_radius=1, color="#A9B8CE", offset=ft.Offset(0, 3)),
        ft.BoxShadow(blur_radius=14, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
        escala_hover=1.02,
    )

    contenido_dialogo = ft.Container(
        width=820, height=670, padding=ft.Padding.symmetric(horizontal=20, vertical=14),
        content=ft.Column(
            [
                encabezado,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [bloque_imagen, ft.Column([campo_nombre, campo_apellidos, bloque_puesto], spacing=14, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)],
                                spacing=20, vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            bloque_telefono,
                            ft.Row([ft.Container(content=campo_correo, expand=True), ft.Container(content=campo_contrasena, expand=True)], spacing=20),
                            _linea_punteada("#09337F", caracter="-", size=12),
                            boton_guardar,
                        ], spacing=14, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ), margin=ft.Margin.only(top=35)
                ),
            ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, tight=True,
        ),
    )

    dialogo = ft.AlertDialog(modal=True, bgcolor=c["bg_card_white"], shape=ft.RoundedRectangleBorder(radius=26), content_padding=0, content=contenido_dialogo)
    page.overlay.append(dialogo)

    # --- Abre el diálogo precargando los datos del empleado ---
    def abrir_dialogo(empleado_a_editar):
        empleado_actual_ref["empleado"] = empleado_a_editar

        partes_nombre = empleado_a_editar.get("nombre", "").split(" ", 1)
        campo_nombre.tf.value = partes_nombre[0] if len(partes_nombre) > 0 else ""
        campo_apellidos.tf.value = partes_nombre[1] if len(partes_nombre) > 1 else ""
        dropdown_puesto.value = empleado_a_editar.get("puesto", PUESTOS_DISPONIBLES[0])

        telefono_guardado = str(empleado_a_editar.get("telefono", "") or "")
        if telefono_guardado.startswith("(") and ")" in telefono_guardado:
            codigo = telefono_guardado[1:telefono_guardado.index(")")].strip("'").strip("(")
            numero = telefono_guardado[telefono_guardado.index(")")+1:]
            campo_telefono.value = ''.join(filter(str.isdigit, numero))[-10:]
        else:
            codigo = "+52"
            campo_telefono.value = ''.join(filter(str.isdigit, telefono_guardado))[-10:]
        
        dropdown_codigo_pais.options = [ft.dropdown.Option(key=c, text=e) for e, c in CODIGOS_PAIS]
        dropdown_codigo_pais.value = codigo
        dropdown_codigo_pais.update()
        campo_telefono.update()
        
        campo_correo.tf.value = empleado_a_editar.get("correo", "")
        campo_contrasena.tf.value = ""

        err_nombre.visible = False
        err_apellidos.visible = False
        err_telefono.visible = False
        err_correo.visible = False

        ruta_imagen_actual = empleado_a_editar.get("imagen")
        imagen_empleado_seleccionada["path"] = ruta_imagen_actual
        if ruta_imagen_actual:
            recuadro_imagen.content = ft.Image(
                src=ruta_imagen_actual, width=TAMANO_RECUADRO_IMAGEN, height=TAMANO_RECUADRO_IMAGEN, fit=ft.BoxFit.COVER, border_radius=12,
            )
        else:
            recuadro_imagen.content = _icono_imagen_vacia()

        dialogo.open = True
        page.update()

        page.update()
        dropdown_codigo_pais.update()

    return dialogo, abrir_dialogo

# ============================================================
# Diálogo: eliminar empleado (confirmación)
# ============================================================
def _construir_dialogo_eliminar_usuario(page: ft.Page, al_eliminar_callback=None):
    c = colores()
    modo_oscuro = ESTADO_UI["modo_oscuro"]
    color_acento = c["border"] if modo_oscuro else "#5C88F2"
    empleado_a_borrar_ref = {"empleado": None}

    def cerrar_dialogo(e=None):
        dialogo.open = False
        page.update()

    texto_advertencia = ft.Text(
        "¿Está segur@ de eliminar al empleado?",
        size=18, weight=ft.FontWeight.BOLD, color=c["input_bg"],
        text_align=ft.TextAlign.CENTER
    )

    # --- Elimina al empleado del nivel correspondiente ---
    def confirmar_eliminacion(e):
        emp = empleado_a_borrar_ref["empleado"]
        if emp:
            UsuarioDAO.eliminar(emp["usuario_id"])
            NIVELES_EJEMPLO[:] = _cargar_niveles()

            if al_eliminar_callback:
                al_eliminar_callback()

            snack = ft.SnackBar(
                content=ft.Text(f"Empleado '{emp['nombre']}' eliminado", color=ft.Colors.WHITE),
                bgcolor="#E53935"
            )
            page.overlay.append(snack)
            snack.open = True

        cerrar_dialogo()

    boton_cancelar = ft.ElevatedButton(
        "Cancelar",
        bgcolor=color_acento,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        height=45,
        expand=True,
        on_click=cerrar_dialogo
    )

    boton_confirmar = ft.ElevatedButton(
        "Eliminar",
        bgcolor="#E53935",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        height=45,
        expand=True,
        on_click=confirmar_eliminacion
    )

    icono_central = ft.Column(
        [
            ft.Icon(ft.Icons.WARNING_ROUNDED, size=36, color=color_acento),
            ft.Icon(ft.Icons.DELETE_OUTLINED, size=28, color=color_acento),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    contenido_dialogo = ft.Container(
        width=420,
        padding=25,
        bgcolor=c["bg_card_white"],
        border_radius=20,
        border=ft.Border.all(2, color_acento),
        content=ft.Column(
            [
                texto_advertencia,
                ft.Container(content=icono_central, alignment=ft.Alignment.CENTER, padding=ft.Padding.symmetric(vertical=10)),
                ft.Row(
                    [boton_cancelar, boton_confirmar],
                    spacing=15,
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        )
    )

    dialogo = ft.AlertDialog(
        modal=True,
        content_padding=0,
        bgcolor=ft.Colors.TRANSPARENT,
        content=contenido_dialogo
    )
    page.overlay.append(dialogo)

    # --- Abre el diálogo mostrando el nombre del empleado a eliminar ---
    def abrir_dialogo(empleado):
        empleado_a_borrar_ref["empleado"] = empleado
        dialogo.open = True
        page.update()

    return dialogo, abrir_dialogo

# ============================================================
# Punto de entrada: vista de Empleados (organigrama piramidal)
# ============================================================
def vista_empleados(page: ft.Page):
    # --- Estado, barra de búsqueda y diálogos ---
    c = colores()
    filtro_puesto_actual = {"puesto": None}
    menu_filtros_visible = {"abierto": False}

    DURACION_ANIM_FILTROS = 260

    contenedor_piramide = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    campo_busqueda = ft.TextField(
        hint_text="Buscar", prefix_icon=ft.Icons.SEARCH, height=40, border_radius=30,
        bgcolor=ft.Colors.WHITE, content_padding=ft.Padding.only(left=10, right=10),
        border_color=c["borde_campo"], color=c["input_bg"], expand=True,
        on_change=lambda e: actualizar_organigrama(),
    )

    def restaurar_filtros(e):
        filtro_puesto_actual["puesto"] = None
        actualizar_organigrama()

    boton_restaurar = ft.ElevatedButton(
        "Restaurar filtros", icon=ft.Icons.FILTER_ALT_OFF, bgcolor=c["boton_secundario"],
        color=ft.Colors.WHITE, visible=False, height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=restaurar_filtros
    )

    _dialogo_agregar, abrir_dialogo_agregar_usuario = _construir_dialogo_agregar_usuario(
        page, al_guardar_callback=lambda: actualizar_organigrama()
    )

    _dialogo_editar, abrir_dialogo_editar_usuario = _construir_dialogo_editar_usuario(
        page, al_guardar_callback=lambda: actualizar_organigrama()
    )

    _dialogo_eliminar, abrir_dialogo_eliminar_usuario = _construir_dialogo_eliminar_usuario(
        page, al_eliminar_callback=lambda: actualizar_organigrama()
    )

    # --- Construye la pirámide de niveles con las tarjetas de empleados ---
    def crear_piramide_con_callbacks(niveles, modo_filtro=False):
        filas_niveles = []
        contador_empleado = 1
        niveles_colores = c["niveles_empleados"]

        for i, nivel in enumerate(niveles):
            color_borde = niveles_colores[i % len(niveles_colores)]
            filas_niveles.append(_encabezado_nivel(nivel["titulo"], len(nivel["empleados"]), color_borde, c))

            for emp in nivel["empleados"]:
                emp["numero"] = contador_empleado
                emp["color_borde"] = color_borde
                contador_empleado += 1

            tarjetas_nivel = [
                ft.Container(
                    content=crear_tarjeta_empleado(
                        emp,
                        on_editar=lambda empleado_obj: abrir_dialogo_editar_usuario(empleado_obj),
                        on_eliminar=lambda empleado_obj: abrir_dialogo_eliminar_usuario(empleado_obj)
                    ),
                    margin=ft.Margin.only(bottom=15)
                )
                for emp in nivel["empleados"]
            ]

            fila_tarjetas = ft.Row(
                controls=tarjetas_nivel, wrap=modo_filtro,
                scroll=None if modo_filtro else ft.ScrollMode.ALWAYS,
                alignment=ft.MainAxisAlignment.START if modo_filtro else ft.MainAxisAlignment.CENTER,
                spacing=15, run_spacing=15 if modo_filtro else 0,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )

            filas_niveles.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=25),
                    content=fila_tarjetas,
                    height=None if modo_filtro else ALTO_FILA_EMPLEADOS,
                )
            )

        return ft.Column(controls=filas_niveles, spacing=5)

    # --- Aplica búsqueda/filtro y redibuja la pirámide (o el mensaje vacío) ---
    def actualizar_organigrama():
        query = campo_busqueda.value.lower().strip() if campo_busqueda.value else ""
        niveles_filtrados = []
        total_encontrados = 0

        for nivel in NIVELES_EJEMPLO:
            if filtro_puesto_actual["puesto"] and nivel["titulo"] != filtro_puesto_actual["puesto"]:
                continue

            empleados_filtrados = [
                emp for emp in nivel["empleados"]
                if query in emp["nombre"].lower()
            ]
            total_encontrados += len(empleados_filtrados)

            niveles_filtrados.append({
                "titulo": nivel["titulo"],
                "empleados": empleados_filtrados
            })

        if total_encontrados == 0:
            mensaje_vacio = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, size=60, color="#5C88F2"),
                        ft.Text("No se encontraron empleados", size=18, color=c["texto_secundario"], weight=ft.FontWeight.W_500),
                        ft.Text("Intenta buscar con otro término o revisa la ortografía.", size=16, color=ft.Colors.GREY_500),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.CENTER, expand=True,
            )
            contenedor_piramide.controls = [mensaje_vacio]
        else:
            esta_filtrado = filtro_puesto_actual["puesto"] is not None
            contenedor_piramide.controls = [crear_piramide_con_callbacks(niveles_filtrados, modo_filtro=esta_filtrado)]

        boton_restaurar.visible = filtro_puesto_actual["puesto"] is not None
        page.update()

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

    async def aplicar_filtro(puesto):
        filtro_puesto_actual["puesto"] = puesto
        menu_filtros_visible["abierto"] = False
        await _cerrar_panel_filtros()
        actualizar_organigrama()

    # --- Botones del panel de filtros por puesto ---
    def crear_boton_filtro(texto):
        async def _on_click(e, t=texto):
            await aplicar_filtro(t)

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
                crear_boton_filtro("Administradores"),
                crear_boton_filtro("Cajeros"),
                crear_boton_filtro("Almacenistas"),
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
        if ESTADO_UI["modo_oscuro"]:
            SOMBRA_NORMAL_PILDORA = ft.BoxShadow(blur_radius=10, spread_radius=1, color=c["sombra"], offset=ft.Offset(0, 3))
            SOMBRA_HOVER_PILDORA = ft.BoxShadow(blur_radius=14, spread_radius=2, color=c["sombra"], offset=ft.Offset(0, 4))
        else:
            SOMBRA_NORMAL_PILDORA = ft.BoxShadow(blur_radius=20, spread_radius=1, color="#A6B9D8", offset=ft.Offset(0, 3))
            SOMBRA_HOVER_PILDORA = ft.BoxShadow(blur_radius=24, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4))
        _aplicar_hover_boton_paginacion(boton, SOMBRA_NORMAL_PILDORA, SOMBRA_HOVER_PILDORA, escala_hover=1.05)
        return boton

    # --- Barra superior: búsqueda + botones Añadir/Filtros ---
    bar_busqueda = ft.Row(
        [
            campo_busqueda,
            _crear_boton_pildora("Añadir", ft.Icons.ADD, abrir_dialogo_agregar_usuario),
            _crear_boton_pildora("Filtros", ft.Icons.FILTER_ALT, toggle_filtros),
        ], spacing=10,
    )

    # --- Ensamblado final: lienzo con la pirámide + panel de filtros superpuesto ---
    lienzo = ft.Container(expand=True, bgcolor=c["fondo_lienzo"], border_radius=15, padding=15, content=contenedor_piramide)
    lienzo_con_boton_flotante = ft.Stack([lienzo, ft.Container(content=boton_restaurar, right=20, bottom=20)], expand=True)

    actualizar_organigrama()

    return ft.Container(
        expand=True,
        content=ft.Stack(
            [
                ft.Column([bar_busqueda, ft.Container(content=lienzo_con_boton_flotante, expand=True)], spacing=15, expand=True),
                panel_flotante_filtros
            ], expand=True
        )
    )