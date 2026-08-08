import math
import tkinter as tk
from tkinter import filedialog

import flet as ft

from theme import colores
from state import ESTADO_UI

CARGOS_DISPONIBLES = ["Administrador", "Gerente", "Farmacéutico", "Cajero", "Almacenista"]

# --- Estado de sesión: se mantiene mientras la app está abierta, sin importar
#     los cambios de pestaña, ya que _vista_perfil se reconstruye en cada cambio ---
_ESTADO_PERFIL_SESION = {"foto": None, "foto_cargada": False}

CODIGOS_PAIS = [
    ("🇲🇽 +52", "+52"),
    ("🇺🇸 +1", "+1"),
    ("🇪🇸 +34", "+34"),
    ("🇨🇴 +57", "+57"),
    ("🇦🇷 +54", "+54"),
]

# --- Helpers de almacenamiento local (persisten valores entre sesiones) ---
def _leer_guardado(page, key, valor_defecto):
    if not page or not key:
        return valor_defecto
    try:
        valor = page.client_storage.get(key)
    except Exception:
        valor = None
    return valor if valor not in (None, "") else valor_defecto

def _guardar(page, key, valor):
    if not page or not key:
        return
    try:
        page.client_storage.set(key, valor)
    except Exception:
        pass

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

# --- Helpers de UI reutilizables (línea punteada, pestañas, selectores, sombra) ---
def _linea_punteada(color):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(-1, 0),
        content=ft.Text(
            "- " * 100,
            color=color,
            size=13,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

def _selector_pestanas(pestana_activa, on_click, c):
    def boton(icono, texto, key):
        activo = pestana_activa == key
        b = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icono, color=ft.Colors.WHITE, size=18),
                    ft.Text(texto, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="#588CEF" if activo else "#97B7F4",
            border_radius=30,
            padding=ft.Padding.symmetric(horizontal=18, vertical=8),
            margin=ft.Margin.symmetric(horizontal=2, vertical=2),
            on_click=lambda e, k=key: on_click(k),
            ink=True,
        )
        _aplicar_hover_boton_paginacion(
            b,
            ft.BoxShadow(blur_radius=20, spread_radius=1, color="#A6B9D8", offset=ft.Offset(0, 3)),
            ft.BoxShadow(blur_radius=24, spread_radius=2, color="#8FA6D0", offset=ft.Offset(0, 4)),
            escala_hover=1.03,
        )
        return b

    return ft.Row(
        [
            boton(ft.Icons.PERSON_OUTLINE, "Perfil", "perfil"),
            boton(ft.Icons.SETTINGS_OUTLINED, "Aplicación", "aplicacion"),
        ],
        spacing=10,
    )

def _selector_dos_opciones(icono, texto_izq, texto_der, valor_actual, on_click, c):
    def opcion(texto, key):
        activo = valor_actual == key
        return ft.Container(
            content=ft.Text(texto, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13),
            bgcolor="#588CEF" if activo else "#97B7F4",
            border_radius=30,
            padding=ft.Padding.symmetric(horizontal=18, vertical=10),
            on_click=lambda e, k=key: on_click(k),
            ink=True,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=1,
                color="#A6B9D8",
                offset=ft.Offset(0, 3),
            ),
        )

    return ft.Row(
        [
            ft.Icon(icono, color=c["input_bg"], size=20),
            opcion(texto_izq, "izq"),
            opcion(texto_der, "der"),
        ],
        spacing=14,
    )

def _con_sombra(control, border_radius=30, expand=False):
    return ft.Container(
        content=control,
        border_radius=border_radius,
        expand=expand,
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=1,
            color="#A6B9D8",
            offset=ft.Offset(0, 3),
        ),
    )

TAM_TEXTO_PERFIL = 18

# --- Campo de texto de solo lectura con etiqueta y sombra ---
def _campo_editable(label, valor_inicial, c, page=None, storage_key=None, **kwargs_textfield):
    valor_inicial = _leer_guardado(page, storage_key, valor_inicial)

    campo = ft.TextField(
        value=valor_inicial,
        read_only=True,
        border_color=c["azul_card"],
        border_radius=30,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=c["bg_card_blue"],
        color=c["input_bg"],
        text_size=TAM_TEXTO_PERFIL,
        **kwargs_textfield,
    )

    columna = ft.Column(
        [
            ft.Text(label, size=TAM_TEXTO_PERFIL, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            _con_sombra(campo),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    return columna, campo

def _placeholder_diagonal(color, size):
    diagonal = size * math.sqrt(2)
    linea = lambda angulo: ft.Container(
        width=diagonal,
        height=1.5,
        bgcolor=color,
        rotate=ft.Rotate(angulo),
    )
    return ft.Stack(
        [linea(math.pi / 4), linea(-math.pi / 4)],
        width=size,
        height=size,
        alignment=ft.Alignment.CENTER,
    )

# ============================================================
# Pestaña "Perfil": foto, datos personales, contacto y contraseña
# ============================================================
def _vista_perfil(page: ft.Page, c):
    # --- Selector de imagen vía tkinter.filedialog (igual que en Inventario) ---
    EXTENSIONES_IMAGEN = [("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]

    def _seleccionar_archivo_imagen():
        raiz = tk.Tk()
        raiz.withdraw()
        raiz.attributes("-topmost", True)
        try:
            ruta = filedialog.askopenfilename(
                title="Selecciona una foto de perfil",
                filetypes=EXTENSIONES_IMAGEN,
            )
        finally:
            raiz.destroy()
        return ruta

    ruta_foto_guardada = _ESTADO_PERFIL_SESION["foto"]
    if not _ESTADO_PERFIL_SESION["foto_cargada"]:
        ruta_foto_guardada = _leer_guardado(page, "perfil_foto", None)
        _ESTADO_PERFIL_SESION["foto"] = ruta_foto_guardada
        _ESTADO_PERFIL_SESION["foto_cargada"] = True

    def _contenido_foto(ruta):
        if ruta:
            return ft.Image(src=ruta, width=210, height=210, fit=ft.BoxFit.COVER, border_radius=12)
        return _placeholder_diagonal(c["azul_card"], 210)

    def _abrir_selector_foto(e):
        ruta = _seleccionar_archivo_imagen()
        if not ruta:
            return

        _ESTADO_PERFIL_SESION["foto"] = ruta
        _guardar(page, "perfil_foto", ruta)
        recuadro_foto.content = _contenido_foto(ruta)
        recuadro_foto.update()

    # --- Bloque de foto de perfil (placeholder + botón de cambio) ---
    recuadro_foto = ft.Container(
        width=210,
        height=210,
        bgcolor=c["bg_card_white"],
        border=ft.Border.all(1.5, c["azul_card"]),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        content=_contenido_foto(ruta_foto_guardada),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ink=True,
        on_click=_abrir_selector_foto,
        tooltip="Agregar imagen desde tus archivos",
    )
    boton_foto = ft.Container(
        content=ft.Icon(ft.Icons.IMAGE_OUTLINED, color=c["azul_card"], size=18),
        bgcolor=c["bg_card_white"],
        shape=ft.BoxShape.CIRCLE,
        padding=8,
        border=ft.Border.all(1.5, c["borde_campo"]),
        tooltip="Agregar imagen desde tus archivos",
        on_click=_abrir_selector_foto,
        ink=True,
    )
    bloque_foto = ft.Column(
        [
            ft.Text("Foto", size=TAM_TEXTO_PERFIL, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            ft.Stack(
                [
                    recuadro_foto,
                    ft.Container(content=boton_foto, top=180, left=180),
                ],
                width=210,
                height=210,
            ),
        ],
        spacing=8,
    )

    # --- Campos de nombre, apellidos y cargo ---
    columna_nombre, campo_nombre = _campo_editable("Nombre", "Diego Saúl", c, page=page, storage_key="perfil_nombre")
    columna_apellidos, campo_apellidos = _campo_editable(
        "Apellidos", "Cervantes Cervantes", c, page=page, storage_key="perfil_apellidos"
    )

    campo_cargo = ft.TextField(
        value="Administrador",
        read_only=True,
        expand=True,
        border_color=c["azul_card"],
        border_radius=30,
        bgcolor=c["bg_card_blue"],
        color=c["input_bg"],
        text_size=TAM_TEXTO_PERFIL,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
    )
    bloque_cargo = ft.Column(
        [
            ft.Text("Cargo", size=TAM_TEXTO_PERFIL, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            _con_sombra(campo_cargo),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    columna_derecha = ft.Column(
        [columna_nombre, columna_apellidos, bloque_cargo],
        spacing=16,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # --- Campo de correo ---
    columna_correo, campo_correo = _campo_editable(
        "Correo electrónico",
        "cervantes@gmail.com",
        c,
        page=page,
        storage_key="perfil_correo",
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    # --- Teléfono: código de país + número ---
    dropdown_codigo_pais = ft.Dropdown(
        value=_leer_guardado(page, "perfil_tel_codigo", "+52"),
        width=165,
        border_color=c["azul_card"],
        border_radius=30,
        bgcolor=c["bg_card_blue"],
        color=c["input_bg"],
        text_size=TAM_TEXTO_PERFIL,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        options=[ft.DropdownOption(key=codigo, text=etiqueta) for etiqueta, codigo in CODIGOS_PAIS],
        disabled=True,
    )

    campo_telefono = ft.TextField(
        value=_leer_guardado(page, "perfil_tel_numero", "242 658 6982"),
        read_only=True,
        border_color=c["azul_card"],
        border_radius=30,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=c["bg_card_blue"],
        color=c["input_bg"],
        text_size=TAM_TEXTO_PERFIL,
        keyboard_type=ft.KeyboardType.PHONE,
        expand=True,
    )

    bloque_telefono = ft.Column(
        [
            ft.Text("Número telefónico", size=TAM_TEXTO_PERFIL, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            ft.Row([dropdown_codigo_pais, _con_sombra(campo_telefono, expand=True)], spacing=8, expand=True),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # --- Contraseña con botón para mostrar/ocultar ---
    campo_contrasena = ft.TextField(
        value=_leer_guardado(page, "perfil_contrasena", "12345678"),
        password=True,
        read_only=True,
        border_color=c["azul_card"],
        border_radius=30,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=c["bg_card_blue"],
        color=c["input_bg"],
        text_size=TAM_TEXTO_PERFIL,
        expand=True,
    )

    def alternar_ver_contrasena(e):
        campo_contrasena.password = not campo_contrasena.password
        campo_contrasena.update()

    boton_ojo = ft.Container(
        content=ft.Icon(ft.Icons.REMOVE_RED_EYE_OUTLINED, color=c["azul_card"], size=20),
        bgcolor=c["bg_card_white"],
        shape=ft.BoxShape.CIRCLE,
        padding=10,
        border=ft.Border.all(1.5, c["borde_campo"]),
        on_click=alternar_ver_contrasena,
        tooltip="Mostrar/ocultar contraseña",
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=1,
            color="#A6B9D8",
            offset=ft.Offset(0, 3),
        ),
    )

    bloque_contrasena = ft.Column(
        [
            ft.Text("Contraseña", size=TAM_TEXTO_PERFIL, weight=ft.FontWeight.BOLD, color=c["input_bg"]),
            ft.Row([_con_sombra(campo_contrasena, expand=True), boton_ojo], spacing=8, expand=True),
        ],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # --- Ensamblado final de la pestaña Perfil ---
    contenedor = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Row(
                    [bloque_foto, columna_derecha],
                    spacing=30,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                ),
                columna_correo,
                bloque_telefono,
                bloque_contrasena,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )
    return contenedor

# ============================================================
# Pestaña "Aplicación": tema, animaciones, transparencia, asistencia
# ============================================================
def _vista_aplicacion(page: ft.Page, c, reconstruir_interfaz):
    estado_ajustes = {"tema": "der" if ESTADO_UI["modo_oscuro"] else "izq", "animaciones": "izq", "transparencia": "izq"}

    def cambiar_tema(k):
        ESTADO_UI["modo_oscuro"] = (k == "der")

        reconstruir_interfaz()

    def cambiar_animaciones(k):
        estado_ajustes["animaciones"] = k
        fila_animaciones.content = _selector_dos_opciones(
            ft.Icons.AUTO_AWESOME_OUTLINED, "Fluidas", "Reducidas", k, cambiar_animaciones, c
        )

        page.update()

    def cambiar_transparencia(k):
        estado_ajustes["transparencia"] = k
        fila_transparencia.content = _selector_dos_opciones(
            ft.Icons.OPACITY_OUTLINED, "Moderadas", "Sólidas", k, cambiar_transparencia, c
        )
        page.update()

    # --- Filas de selección (tema, animaciones, transparencia) ---
    fila_tema = ft.Container(content=_selector_dos_opciones(ft.Icons.LIGHT_MODE_OUTLINED, "Claro", "Oscuro", estado_ajustes["tema"], cambiar_tema, c))
    fila_animaciones = ft.Container(content=_selector_dos_opciones(ft.Icons.AUTO_AWESOME_OUTLINED, "Fluidas", "Reducidas", "izq", cambiar_animaciones, c))
    fila_transparencia = ft.Container(content=_selector_dos_opciones(ft.Icons.OPACITY_OUTLINED, "Moderadas", "Sólidas", "izq", cambiar_transparencia, c))

    def _fila_ajuste(etiqueta, control):
        return ft.Row(
            [ft.Text(etiqueta, size=14, weight=ft.FontWeight.BOLD, color=c["input_bg"], width=200), control],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
        )

    def _boton_asistencia(texto, url):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(texto, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Icon(ft.Icons.OPEN_IN_NEW, color=ft.Colors.WHITE, size=16),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor="#588CEF",
            border_radius=30,
            padding=14,
            width=340,
            on_click=lambda e: page.launch_url(url),
            ink=True,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=1,
                color="#A6B9D8",
                offset=ft.Offset(0, 3),
            ),
        )

    # --- Ensamblado final de la pestaña Aplicación ---
    return ft.Container(
        padding=30,
        content=ft.Column(
            [
                _fila_ajuste("Color de tema", fila_tema),
                _fila_ajuste("Animaciones", fila_animaciones),
                _fila_ajuste("Transparencia de botones", fila_transparencia),
                _linea_punteada(c["input_bg"]),
                ft.Row(
                    [
                        ft.Text("Asistencia", size=14, weight=ft.FontWeight.BOLD, color=c["input_bg"], width=200),
                        ft.Column(
                            [

                                _boton_asistencia("Centro de asistencia", "https://example.com/soporte"),
                                _boton_asistencia("Sitio web", "https://example.com"),
                                _boton_asistencia("Condiciones de servicio", "https://example.com/terminos"),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=40,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=30,
            scroll=ft.ScrollMode.AUTO,
        ),
    )

# ============================================================
# Punto de entrada: vista de Ajustes con selector de pestañas
# ============================================================
def vista_ajustes(page: ft.Page, reconstruir_interfaz):
    c = colores()
    area_contenido = ft.Container(expand=True)
    selector_container = ft.Container()

    # --- Cambia entre la pestaña Perfil y Aplicación ---
    def cambiar_pestana(key):
        selector_container.content = _selector_pestanas(key, cambiar_pestana, c)
        area_contenido.content = (
            _vista_perfil(page, c) if key == "perfil" else _vista_aplicacion(page, c, reconstruir_interfaz)
        )
        page.update()

    cambiar_pestana("perfil")

    # --- Contenedor raíz: selector de pestañas + contenido dinámico ---
    return ft.Container(
        expand=True,
        content=ft.Column(
            [
                selector_container,
                ft.Container(bgcolor=c["fondo_lienzo"], border_radius=15, expand=True, content=area_contenido),
            ],
            spacing=20,
            expand=True,
        ),
    )