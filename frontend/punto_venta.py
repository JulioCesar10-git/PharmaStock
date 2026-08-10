import flet as ft
import asyncio
from datetime import datetime
from decimal import Decimal

from frontend.theme import colores

# IMPORTAR BACKEND
from backend.dao.medicamento_dao import MedicamentoDAO
from backend.dao.producto_dao import ProductoDAO

from backend.dao.venta_dao import VentaDAO
from backend.models.venta import Venta

from backend.services.email_sender import enviar_ticket_por_correo

import uuid

ticket_items = []
producto_seleccionado = None
cobro_activo = False
venta_completada = False
procesando_cobro = False  # evita que procesar_cobro() se ejecute dos veces en paralelo

def border_all(width, color):
    side = ft.BorderSide(width=width, color=color)
    return ft.Border(top=side, right=side, bottom=side, left=side)

DIAS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

def fecha_larga_es(dt):
    """Devuelve algo como: 'sábado , 08 de agosto de 2026' sin depender del locale del sistema."""
    dia_semana = DIAS_ES[dt.weekday()]
    mes = MESES_ES[dt.month - 1]
    return f"{dia_semana} , {dt.day:02d} de {mes} de {dt.year}"



def main(page: ft.Page, on_salir=None):
    page.title = "Punto de venta"
    page.bgcolor = "white"
    page.padding = 10
    page.window.width = 1366
    page.window.height = 768
    page.window.maximized = True
    page.fonts = {"Quicksand": "https://raw.githubusercontent.com/google/fonts/main/ofl/quicksand/Quicksand[wght].ttf"}
    page.theme = ft.Theme(
        font_family="Quicksand",
        text_theme=ft.TextTheme(
            body_large=ft.TextStyle(weight=ft.FontWeight.W_600, color="black"),
            body_medium=ft.TextStyle(weight=ft.FontWeight.W_600, color="black"),
            body_small=ft.TextStyle(weight=ft.FontWeight.W_600, color="black"),
            label_large=ft.TextStyle(weight=ft.FontWeight.W_600, color="black"),
        ),
    )

    # ============================================================
    # 1. CREAR TODOS LOS CONTROLES PRIMERO
    # ============================================================
    
    # Crear cantidad_display (se usa en las funciones)
    cantidad_display = ft.Container(
        content=ft.Text("1", size=16, color="#1565c0"),
        alignment=ft.Alignment(0, 0), 
        expand=1,
    )
    
    # Crear nombre_producto_display (se usa en las funciones)
    nombre_producto_display = ft.TextField(
        hint_text="Nombre del producto",
        hint_style=ft.TextStyle(size=12, color="#A9C2E8"),
        width=300,
        height=40,
        border=border_all(2, "#5086EC"),
        bgcolor="white",
        border_radius=14,
        text_size=14,
        content_padding=ft.Padding(left=15, top=5, right=15, bottom=5),
        read_only=True,
        value="",
    )
    # Campo de monto recibido
    monto_focus = {"activo": False}
    campo_activo = {"control": None}  # Rastrea qué campo (monto o código de barras) debe recibir el numpad

    monto_recibido_input = ft.TextField(
        hint_text="Monto recibido",
        hint_style=ft.TextStyle(size=12, color="#A9C2E8"),
        border=ft.InputBorder.NONE,  # Sin borde porque ya tiene el Container
        text_size=14,
        expand=True,
        content_padding=ft.Padding(left=5, top=0, right=5, bottom=0),
        on_submit=lambda e: procesar_cobro(),  # Al presionar Enter, procesa el cobro
        on_focus=lambda e: (
            monto_focus.update(activo=True),
            campo_activo.update(control=monto_recibido_input),
            setattr(monto_recibido_input, "hint_text", ""),  # Oculta el placeholder al enfocar
            monto_recibido_input.update(),
        ),
        on_blur=lambda e: (
            monto_focus.update(activo=False),
            campo_activo.update(control=None) if campo_activo["control"] is monto_recibido_input else None,
            setattr(monto_recibido_input, "hint_text", "Monto recibido") if not monto_recibido_input.value else None,  # Restaura el placeholder si quedó vacío
            monto_recibido_input.update(),
        ),
        disabled=True,  # Inicia deshabilitado
        read_only=True,  # Todo el ingreso pasa por digito_presionado (numpad o teclado físico)
        value="",
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^[0-9.]*$",  
        ),
    )
    
    # Crear ticket_body (se usa en actualizar_ticket)
    ticket_body = ft.Container(
        bgcolor="#EDF5FC",
        padding=20,
        expand=True,
        border_radius=14,
        content=ft.Column(
            [],
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    
    # Crear total_box (se usa en actualizar_ticket)
    total_box = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Column(
            [
                ft.Text("Artículos 0", size=22, color="black"),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Subtotal $0.00", size=13, color="grey"),
                                ft.Text("Impuesto $0.00", size=13, color="grey"),
                                ft.Text("Total $0.00", size=26, color="#1565c0", weight=ft.FontWeight.BOLD),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Image(
                            src="Logo_PharmaStockCompleto_SinFondo(Letras).png",
                            width=200,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
        ),
    )
    email_input = ft.TextField(
        hint_text="correo@ejemplo.com",
        hint_style=ft.TextStyle(size=12, color="#3B71E8"),
        text_style=ft.TextStyle(size=12, color="#3B71E8"),
        text_align=ft.TextAlign.CENTER,
        border=ft.InputBorder.NONE,
        text_size=14,
        width=float("inf"),
        content_padding=ft.Padding(left=5, top=0, right=5, bottom=0),
        on_submit=lambda e: enviar_ticket_email(),
        on_change=lambda e: limpiar_error_email(),
        value="",
        disabled = True,
    )

    # Texto de error en rojo para las validaciones del correo (no usamos error_text
    # porque no está disponible en esta versión de Flet)
    email_error_text = ft.Text(
        "",
        size=11,
        color="red",
        text_align=ft.TextAlign.CENTER,
        visible=False,
    )

    enviar_email_btn = ft.ElevatedButton(
        "Enviar",
        bgcolor="#4F7FE0",
        color="white",
        expand=True,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
        on_click=lambda e: enviar_ticket_email(),
        disabled=True,  
    )

    # ============================================================
    # 2. DEFINIR TODAS LAS FUNCIONES
    # ============================================================

    def bloqueado_por_cobro():
    #Muestra aviso y devuelve True si hay un cobro en proceso (bloquea la acción)."""
        if cobro_activo:
            page.show_dialog(ft.SnackBar(ft.Text("Finaliza el cobro actual para continuar")))
            page.update()
            return True
        if venta_completada:
            page.show_dialog(ft.SnackBar(ft.Text("Haz clic en 'Nuevo' para iniciar otro ticket")))
            page.update()
            return True
        return False
    
    def seleccionar_producto(codigo):
        global producto_seleccionado
        if bloqueado_por_cobro():
            return
        for item in ticket_items:
            if item["codigo"] == codigo:
                producto_seleccionado = item
                nombre_producto_display.value = f"► {item['nombre']} (seleccionado)"
                cantidad_display.content = ft.Text(str(item["cantidad"]), size=16, color="#1565c0")
                actualizar_ticket()
                page.show_dialog(ft.SnackBar(ft.Text(f"Seleccionado: {item['nombre']}")))
                page.update()
                return

    def agregar_cantidad():
        global producto_seleccionado
        if bloqueado_por_cobro():
            return
        if producto_seleccionado is None:
            page.show_dialog(ft.SnackBar(ft.Text("Selecciona un producto primero")))
            page.update()
            return
        for item in ticket_items:
            if item["codigo"] == producto_seleccionado["codigo"]:
                item["cantidad"] += 1
                cantidad_display.content = ft.Text(str(item["cantidad"]), size=16, color="#1565c0")
                actualizar_ticket()
                nombre_producto_display.value = f"► {item['nombre']} (seleccionado)"
                page.update()
                return

    def quitar_cantidad():
        global producto_seleccionado
        if bloqueado_por_cobro():
            return
        if producto_seleccionado is None:
            page.show_dialog(ft.SnackBar(ft.Text("Selecciona un producto primero")))
            page.update()
            return
        for i, item in enumerate(ticket_items):
            if item["codigo"] == producto_seleccionado["codigo"]:
                if item["cantidad"] > 1:
                    item["cantidad"] -= 1
                    cantidad_display.content = ft.Text(str(item["cantidad"]), size=16, color="#1565c0")
                    actualizar_ticket()
                    nombre_producto_display.value = f"► {item['nombre']} (seleccionado)"
                    page.update()
                else:
                    page.show_dialog(ft.SnackBar(ft.Text("¿Eliminar producto? Usa el botón Eliminar")))
                    page.update()
                return

    def eliminar_producto():
        global producto_seleccionado
        if bloqueado_por_cobro():
            return
        if producto_seleccionado is None:
            page.show_dialog(ft.SnackBar(ft.Text("Selecciona un producto primero")))
            page.update()
            return
        ticket_items[:] = [item for item in ticket_items if item["codigo"] != producto_seleccionado["codigo"]]
        producto_seleccionado = None
        nombre_producto_display.value = ""
        cantidad_display.content = ft.Text("1", size=16, color="#1565c0")
        actualizar_ticket()
        page.show_dialog(ft.SnackBar(ft.Text("Producto eliminado")))
        page.update()

    def agregar_al_ticket(producto, cantidad=1):
        for item in ticket_items:
            if item["codigo"] == producto["codigo"]:
                item["cantidad"] += cantidad
                actualizar_ticket()
                return
        ticket_items.append({
            "codigo": producto["codigo"],
            "nombre": producto["nombre"],
            "presentacion": producto["presentacion"],
            "precio": producto["precio"],
            "cantidad": cantidad,
            "id": producto.get("id"),
            "tipo": producto.get("tipo", "prod")
        })
        actualizar_ticket()

    def actualizar_ticket():
        if not ticket_items:
            monto_recibido_input.disabled = True
            monto_recibido_input.value = ""

        total_articulos = sum(item["cantidad"] for item in ticket_items)
        total = sum(item["precio"] * item["cantidad"] for item in ticket_items)
        subtotal = round(total / 1.16, 2)
        impuesto = round(total - subtotal, 2)
        total = round(total, 2)

        ticket_body.content.controls.clear()

        if cobro_activo:
            # Ticket bloqueado: se pinta del color del subrayado y no se puede interactuar
            ticket_body.bgcolor = "#1565c0"
            ticket_body.content.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.LOCK, color="white", size=40),
                            ft.Text("PROCESANDO COBRO", size=24, color="white", weight=ft.FontWeight.BOLD),
                            ft.Image(src="PharmaStock_LogoOscuro_3.png", width=140, height=140, fit="contain"),
                            ft.Text(f"Total a cobrar: ${total:.2f}", size=18, color="white"),
                            ft.Text("Ingresa el monto recibido para continuar", size=14, color="white"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            )
            total_box.content.controls[0].value = f"Artículos {total_articulos}"
            total_box.content.controls[1].controls[0].controls[0].value = f"Subtotal ${subtotal:.2f}"
            total_box.content.controls[1].controls[0].controls[1].value = f"Impuesto ${impuesto:.2f}"
            total_box.content.controls[1].controls[0].controls[2].value = f"Total ${total:.2f}"
            page.update()
            return

        ticket_body.bgcolor = "#EDF5FC"
        ticket_body.content.controls.append(
            ft.Text(f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", size=20, color="black")
        )
        ticket_body.content.controls.append(ft.Container(height=15))
        if ticket_items:
            for item in ticket_items:
                nombre_display = f"   {item['cantidad']} {item['nombre']}"
                precio_total = f"${item['precio'] * item['cantidad']:.2f}"
                es_seleccionado = (
                    producto_seleccionado is not None
                    and producto_seleccionado["codigo"] == item["codigo"]
                )
                ticket_body.content.controls.append(
                    linea_producto(
                        nombre_display,
                        precio_total,
                        item['presentacion'],
                        f"${item['precio']:.2f}",
                        item['codigo'],
                        es_seleccionado,
                        venta_completada
                    )
                )
        else:
            ticket_body.content.controls.append(
                ft.Text("No hay productos", size=20, color="gray", italic=True)
            )
        ticket_body.content.controls.append(ft.Container(height=10))
        ticket_body.content.controls.append(
            ft.Text(f"# Artículos : {total_articulos}", size=18, color="black")
        )
        ticket_body.content.controls.append(ft.Container(height=10))
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Subtotal   :", size=20, color="black"),
                    ft.Text(f"${subtotal:.2f}", size=20, color="black")], spacing=10)
        )
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Impuesto   :", size=20, color="black"),
                    ft.Text(f"${impuesto:.2f}", size=20, color="black")], spacing=10)
        )
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Total      :", size=20, color="black"),
                    ft.Text(f"${total:.2f}", size=20, color="#1565c0", weight=ft.FontWeight.BOLD)], spacing=10)
        )
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Recibido :", size=20, color="black"),
                    ft.Text("$0.00", size=20, color="black")], spacing=10)
        )
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Efectivo :", size=20, color="black"),
                    ft.Text("$0.00", size=20, color="black")], spacing=10)
        )
        ticket_body.content.controls.append(
            ft.Row([ft.Container(width=60), ft.Text("Su Cambio:", size=20, color="black"),
                    ft.Text("$0.00", size=20, color="black")], spacing=10)
        )
        ticket_body.content.controls.append(ft.Container(height=10))
        if total > 0:
            monto_letra = f"{int(total)} PESOS {int((total % 1) * 100):02d}/100 MN"
        else:
            monto_letra = "CERO PESOS 00/100 MN"
        ticket_body.content.controls.append(
            ft.Text(monto_letra, size=20, color="black")
        )
        ticket_body.content.controls.append(ft.Container(height=25))
        ticket_body.content.controls.append(
            ft.Row([ft.Container(expand=True), ft.Text("FACTURAS WHASTAPP ###-###-##-##", size=20, color="black")])
        )
        total_box.content.controls[0].value = f"Artículos {total_articulos}"
        total_box.content.controls[1].controls[0].controls[0].value = f"Subtotal ${subtotal:.2f}"
        total_box.content.controls[1].controls[0].controls[1].value = f"Impuesto ${impuesto:.2f}"
        total_box.content.controls[1].controls[0].controls[2].value = f"Total ${total:.2f}"
        page.update()

    def limpiar_ticket():

        global producto_seleccionado, cobro_activo, venta_completada
        nonlocal folio_actual  # folio_actual vive en main(), no es global del módulo
        if cobro_activo:
            page.show_dialog(ft.SnackBar(ft.Text("Finaliza el cobro actual para continuar")))
            page.update()
            return  
        folio_actual = "V-" + str(uuid.uuid4())[:8].upper()
        ticket_header.content.value = f"TICKET       FOLIO: {folio_actual}"
        ticket_header.update()
        ticket_items.clear()
        producto_seleccionado = None
        cobro_activo = False
        venta_completada = False
        nombre_producto_display.value = ""
        cantidad_display.content = ft.Text("1", size=16, color="#1565c0")
        monto_recibido_input.disabled = True  
        monto_recibido_input.value = ""
        email_input.disabled = True
        email_input.value =""
        email_error_text.value = ""
        email_error_text.visible = False
        enviar_email_btn.disabled = True
        actualizar_ticket()
        page.update()

    def procesar_codigo_barras(codigo):
        if bloqueado_por_cobro():
            codigo_barras_input.value = ""
            page.update()
            return
        if codigo:
            # Buscar primero en medicamentos
            med = MedicamentoDAO.obtener_por_codigo_barras(codigo)
            if med:
                producto = {
                    "codigo": med.med_codBarras,
                    "nombre": med.med_nombreGen,
                    "presentacion": med.med_fraccion or "",
                    "precio": float(med.med_precio),
                    "tipo": "med",
                    "id": med.med_id
                }
                nombre_producto_display.value = producto["nombre"]
                agregar_al_ticket(producto)
                page.show_dialog(ft.SnackBar(ft.Text(f"✓ {producto['nombre']} agregado")))
            else:
                # Buscar en productos
                prod = ProductoDAO.obtener_por_codigo_barras(codigo)
                if prod:
                    producto = {
                        "codigo": prod.prod_codBarras,
                        "nombre": prod.prod_nombre,
                        "presentacion": prod.prod_fraccion or "",
                        "precio": float(prod.prod_precio),
                        "tipo": "prod",
                        "id": prod.prod_id
                    }
                    nombre_producto_display.value = producto["nombre"]
                    agregar_al_ticket(producto)
                    page.show_dialog(ft.SnackBar(ft.Text(f"✓ {producto['nombre']} agregado")))
                else:
                    nombre_producto_display.value = ""
                    page.show_dialog(ft.SnackBar(ft.Text("Producto no encontrado")))
            codigo_barras_input.value = ""
            page.update()

    def linea_producto(nombre, precio, pieza, pieza_precio, codigo, seleccionado = False,bloqueado = False):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                nombre,
                                size = 17, 
                                weight =ft.FontWeight.BOLD if seleccionado else ft.FontWeight.NORMAL,
                            ),
                            ft.Text(precio, size = 17),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text(pieza, size=17),
                            ft.Text(pieza_precio, size=17),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=0,
            ),
            padding= ft.Padding(left = 10, top = 6, right = 10, bottom = 8),
            margin=ft.Margin(left=0, top=0, right=0, bottom=4),
            bgcolor = "#D6E6FA" if seleccionado else ("#F4F9FF" if not bloqueado else "#E8EEF7"),
            border = ft.Border(bottom=ft.BorderSide(2, "#1565c0")) if seleccionado else border_all(1, "#C9DCF5"),
            border_radius=8,
            ink=not bloqueado,
            on_click=None if bloqueado else (lambda e: seleccionar_producto(codigo)),
        )
    async def activar_monto_recibido(e=None):
        global cobro_activo
        if venta_completada:
            page.show_dialog(ft.SnackBar(ft.Text("Haz clic en 'Nuevo' para iniciar otro ticket")))
            page.update()
            return
    #Activa el campo de monto recibido y le da foco
        if not ticket_items:
            page.show_dialog(ft.SnackBar(ft.Text("No hay productos para cobrar")))
            page.update()
            return
        if not monto_recibido_input.disabled:
            procesar_cobro()
            return
    
        monto_recibido_input.disabled = False
        monto_recibido_input.value = ""
        cobro_activo = True
        actualizar_ticket()

        await monto_recibido_input.focus()
        page.update()
        page.show_dialog(ft.SnackBar(ft.Text("Ingresa el monto recibido")))
        page.update()

    def procesar_cobro():
        global cobro_activo, venta_completada, procesando_cobro
        nonlocal folio_actual  # misma variable que usa main()/limpiar_ticket(), no un global del módulo

        # --- Bloqueo anti doble-envío ---------------------------------
        # Cobrar puede dispararse por 3 caminos distintos (botón "Cobrar",
        # Enter en el campo de monto, Enter físico/numpad). Si dos de esos
        # eventos llegan casi al mismo tiempo, sin esta bandera se ejecutaría
        # procesar_cobro() dos veces con el MISMO folio_actual y el segundo
        # INSERT chocaría con la restricción de unicidad de venta_folio.
        if procesando_cobro:
            return
        procesando_cobro = True

        try:
            if not ticket_items:
                page.show_dialog(ft.SnackBar(ft.Text("No hay productos para cobrar")))
                page.update()
                return

            total = round(sum(item["precio"] * item["cantidad"] for item in ticket_items), 2)

            valor = monto_recibido_input.value.strip()
            if not valor:
                page.show_dialog(ft.SnackBar(ft.Text("Ingresa un monto válido")))
                page.update()
                return

            try:
                valor_limpio = valor.replace("$", "").replace(",", "").strip()
                monto_recibido = float(valor_limpio)
            except ValueError:
                page.show_dialog(ft.SnackBar(ft.Text("Ingresa un monto válido")))
                page.update()
                return

            if monto_recibido < total:
                page.show_dialog(ft.SnackBar(ft.Text(f"Monto insuficiente. Total: ${total:.2f}")))
                page.update()
                return

            cambio = monto_recibido - total

            # Preparar datos de la venta
            carrito_bd = [{
                "producto_id": item["id"],
                "tipo": item["tipo"],
                "cantidad": item["cantidad"],
                "precio_unitario": Decimal(str(item["precio"])),
                "subtotal": Decimal(str(item["precio"] * item["cantidad"])),
                "nombre": item["nombre"]
            } for item in ticket_items]

            total_bd = Decimal(str(total))
            subtotal_sin_iva = round(total_bd / Decimal("1.16"), 2)
            iva_bd = round(total_bd - subtotal_sin_iva, 2)

            # --- Guardar venta en BD, con un reintento si el folio choca ---
            intentos_restantes = 2
            guardado_ok = False
            ultimo_error = None

            while intentos_restantes > 0 and not guardado_ok:
                intentos_restantes -= 1
                venta_obj = Venta(
                    venta_folio=folio_actual,
                    venta_fecha=None,
                    venta_usuario_id=None,
                    venta_subtotal=subtotal_sin_iva,
                    venta_iva=iva_bd,
                    venta_total=total_bd,
                    venta_pago=Decimal(str(monto_recibido)),
                    venta_cambio=Decimal(str(cambio))
                )
                try:
                    VentaDAO.crear_venta(venta_obj, carrito_bd)
                    guardado_ok = True
                except Exception as ex:
                    ultimo_error = ex
                    mensaje = str(ex).lower()
                    es_folio_duplicado = "venta_folio" in mensaje or "llave duplicada" in mensaje or "unique" in mensaje
                    if es_folio_duplicado and intentos_restantes > 0:
                        # El folio ya existía en la BD: generamos uno nuevo y
                        # reintentamos una sola vez en lugar de perder la venta.
                        folio_actual = "V-" + str(uuid.uuid4())[:8].upper()
                        ticket_header.content.value = f"TICKET       FOLIO: {folio_actual}"
                        ticket_header.update()
                    else:
                        break  # error real (no de folio) o ya sin reintentos

            if not guardado_ok:
                # No se guardó: NO marcamos la venta como completada ni
                # avisamos "éxito". El usuario puede volver a intentar.
                print(f"Error al guardar venta: {ultimo_error}")
                page.show_dialog(
                    ft.SnackBar(ft.Text("No se pudo guardar la venta. Intenta cobrar de nuevo."))
                )
                page.update()
                return

            # Solo si el INSERT fue exitoso marcamos la venta como completada
            cobro_activo = False
            venta_completada = True
            actualizar_ticket()
            actualizar_ticket_con_pago(monto_recibido, cambio)

            monto_recibido_input.disabled = True
            monto_recibido_input.value = ""
            email_input.disabled = False
            enviar_email_btn.disabled = False
            page.update()

            page.show_dialog(ft.SnackBar(ft.Text(f"¡Cobro exitoso! Cambio: ${cambio:.2f}")))
            page.update()

        finally:
            procesando_cobro = False

    def digito_presionado(valor):
        """Inserta un dígito/punto o borra el último carácter en el campo actualmente
        activo (código de barras o monto recibido, el que se haya clicado/enfocado)."""
        campo = campo_activo["control"]

        if campo is None:
            page.show_dialog(ft.SnackBar(ft.Text("Selecciona el campo de código de barras o de monto primero")))
            page.update()
            return

        if campo is monto_recibido_input and monto_recibido_input.disabled:
            page.show_dialog(ft.SnackBar(ft.Text("Presiona 'Cobrar' para ingresar el monto")))
            page.update()
            return

        actual = campo.value or ""

        if valor == "⌫":
            actual = actual[:-1]
        elif valor == ".":
            if "." not in actual:
                actual += "."
        else:
            actual += valor

        campo.value = actual
        campo.update()

    def manejar_teclado(e: ft.KeyboardEvent):
        """Conecta el teclado físico con las mismas acciones del numpad en pantalla,
        pero solo cuando el campo de monto recibido tiene el foco (para no interferir
        con el código de barras u otros campos de texto). Reconoce tanto el renglón
        superior de números como las teclas del numpad (teclado numérico)."""
        if not monto_focus["activo"]:
            return

        key = e.key

        # Variantes con las que distintas plataformas reportan las teclas del numpad
        numpad_digitos = {
            "Numpad 0": "0", "Numpad 1": "1", "Numpad 2": "2", "Numpad 3": "3",
            "Numpad 4": "4", "Numpad 5": "5", "Numpad 6": "6", "Numpad 7": "7",
            "Numpad 8": "8", "Numpad 9": "9",
            "Numpad0": "0", "Numpad1": "1", "Numpad2": "2", "Numpad3": "3",
            "Numpad4": "4", "Numpad5": "5", "Numpad6": "6", "Numpad7": "7",
            "Numpad8": "8", "Numpad9": "9",
        }

        if key in numpad_digitos:
            digito_presionado(numpad_digitos[key])
        elif key and key in "0123456789":
            digito_presionado(key)
        elif key in (".", "Numpad Decimal", "NumpadDecimal", "Decimal"):
            digito_presionado(".")
        elif key in ("Backspace", "Numpad Backspace", "NumpadBackspace"):
            digito_presionado("⌫")
        elif key in ("Enter", "Numpad Enter", "NumpadEnter"):
            procesar_cobro()

    page.on_keyboard_event = manejar_teclado

    def actualizar_ticket_con_pago(monto_recibido, cambio):
        for i, control in enumerate(ticket_body.content.controls):
            if isinstance(control, ft.Row) and len(control.controls) >= 3:
                if "Recibido :" in control.controls[1].value:
                    control.controls[2].value = f"${monto_recibido:.2f}"
                elif "Su Cambio:" in control.controls[1].value:
                    control.controls[2].value = f"${cambio:.2f}"
        page.update()

    def limpiar_error_email():
        """Quita el mensaje de error en rojo del campo de correo mientras el usuario escribe."""
        if email_error_text.visible:
            email_error_text.value = ""
            email_error_text.visible = False
            email_error_text.update()

    def mostrar_error_email(mensaje):
        email_error_text.value = mensaje
        email_error_text.visible = True
        email_error_text.update()

    def enviar_ticket_email():
    #Envía el ticket por correo electrónico
        if not venta_completada:
            page.show_dialog(ft.SnackBar(ft.Text("Completa el cobro antes de enviar el ticket")))
            page.update()
            return
        if not ticket_items:
            page.show_dialog(ft.SnackBar(ft.Text("No hay productos en el ticket para enviar")))
            page.update()
            return

        email = email_input.value or ""

        if not email.strip():
            mostrar_error_email("Ingresa un correo electrónico")
            return

        # Validación: no se permiten espacios en el correo
        if " " in email:
            mostrar_error_email("No puedes dejar espacios en el correo")
            return

        # Validación: el correo debe contener un @
        if "@" not in email:
            mostrar_error_email("Recuerda colocar un @ en el correo")
            return

        # Correo válido: se quita cualquier error previo
        limpiar_error_email()
        
        # Construir el contenido del ticket
        total_articulos = sum(item["cantidad"] for item in ticket_items)
        total = sum(item["precio"] * item["cantidad"] for item in ticket_items)
        subtotal = round(total / 1.16, 2)
        impuesto = round(total - subtotal, 2)
        total = round(total, 2)

        ticket_text = "=================================\n"
        ticket_text += "        TICKET DE COMPRA\n"
        ticket_text += "================================\n"
        ticket_text += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        ticket_text += f"Folio: {folio_actual}\n"
        ticket_text += "--------------------------------\n"

        for item in ticket_items:
            ticket_text += f"{item['cantidad']} x {item['nombre']}\n"
            ticket_text += f"   ({item['presentacion']}) ${item['precio']:.2f} c/u\n"
            ticket_text += f"   Subtotal: ${item['precio'] * item['cantidad']:.2f}\n"

        ticket_text += "--------------------------------\n"
        ticket_text += f"Articulos: {total_articulos}\n"
        ticket_text += f"Subtotal:  ${subtotal:.2f}\n"
        ticket_text += f"Impuesto:  ${impuesto:.2f}\n"
        ticket_text += f"TOTAL:     ${total:.2f}\n"
        ticket_text += "================================\n"
        ticket_text += "       Gracias por su compra\n"
        ticket_text += "         PHARMA STOCK\n"
        ticket_text += "           FARMACIA\n"
        ticket_text += "================================\n"
        
        # Mostrar en consola para depuración
        print(ticket_text)
        
        # Aquí iría la lógica real de envío de correo
        # Notificación en la parte inferior confirmando el envío
        folio = ticket_header.content.value.split("FOLIO:")[-1].strip()
        enviar_ticket_por_correo(email, ticket_text, folio)
        page.show_dialog(ft.SnackBar(ft.Text(f"✓ Ticket enviado correctamente a {email}")))
        
        # Limpiar campo después de enviar
        email_input.value = ""
        page.update()

    def salir_pos(e):
        #Pide confirmación antes de cerrar sesión y regresar al login
        c = colores()

        def cerrar_dialogo_salir(e_click):
            modal_confirmacion_salir.open = False
            page.update()

        def confirmar_salir(e_click):
            modal_confirmacion_salir.open = False
            page.update()
            if on_salir:
                on_salir()
            else:
                page.controls.clear()
                page.update()

        btn_cancelar_salir = ft.Container(
            content=ft.Text("Cancelar", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=30,
            bgcolor=c["boton_secundario"],
            on_click=cerrar_dialogo_salir,
            ink=True,
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

        btn_confirmar_salir = ft.Container(
            content=ft.Text("Cerrar sesión", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=30,
            bgcolor=c["text_red"],
            on_click=confirmar_salir,
            ink=True,
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

        modal_confirmacion_salir = ft.AlertDialog(
            title=ft.Text(
                "Confirmar cierre de sesión",
                color=c["input_bg"],
                weight=ft.FontWeight.BOLD,
                size=22,
                text_align=ft.TextAlign.CENTER,
            ),
            title_padding=ft.Padding.only(left=24, top=24, right=24, bottom=0),
            content=ft.Container(
                width=450,
                content=ft.Text(
                    "¿Está segur@ de cerrar la sesión?",
                    color=c["input_bg"],
                    size=18,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            actions=[
                ft.Container(
                    width=450,
                    content=ft.Row(
                        [btn_cancelar_salir, btn_confirmar_salir],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20,
                    ),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.overlay.append(modal_confirmacion_salir)
        modal_confirmacion_salir.open = True
        page.update()

    # ============================================================
    # 3. CREAR EL RESTO DE LA UI
    # ============================================================

    # ---------------------------------------------------------------
    # PANEL IZQUIERDO: TICKET
    # ---------------------------------------------------------------

    folio_actual = "V-" + str(uuid.uuid4())[:8].upper()

    ticket_header = ft.Container(
    content=ft.Text(f"TICKET       FOLIO: {folio_actual}",
                     color="black", size=14, weight=ft.FontWeight.BOLD),
    bgcolor="#EDF5FC",
    padding=ft.Padding(left=10, top=6, right=10, bottom=6),
    border_radius=14,
)

    ticket_panel = ft.Container(
        content=ft.Column([ticket_header, ticket_body], spacing=0, expand=True),
        expand=1,
    )

    # ---------------------------------------------------------------
    # PANEL DERECHO: POS
    # ---------------------------------------------------------------

    salir_btn = ft.Container(
        height=36,
        padding=ft.Padding.symmetric(horizontal=14, vertical=0),
        border_radius=18,
        bgcolor="white",
        alignment=ft.Alignment.CENTER,
        content=ft.Row(
            [
                ft.Icon(ft.Icons.MEETING_ROOM_OUTLINED, color="#5086EC", size=20),
                ft.Text("Salir", color="#5086EC", size=14, weight=ft.FontWeight.W_600),
            ],
            spacing=6,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        on_click=salir_pos,
        ink=True,
        tooltip="Cerrar sesión",
    )

    top_bar = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Row(
            [
                ft.Text(datetime.now().strftime("%I:%M %p").lower(), color="#0B2B63", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(fecha_larga_es(datetime.now()), size=14, color="black"),
                ft.Container(expand=True),
                salir_btn,
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    # Panel de envío de ticket por correo
    email_box = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Column(
            [

                ft.Text("Enviar ticket por correo", size=14, color="black", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=email_input,
                    width=float("inf"),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(
                    content=email_error_text,
                    width=float("inf"),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Row(
                    [
                        enviar_email_btn,
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # Campo de código de barras
    codigo_barras_input = ft.TextField(
        hint_text="Código de barras",
        hint_style=ft.TextStyle(size=12, color="#A9C2E8"),
        width=300,
        height=40,
        border=border_all(2, "#5086EC"),
        bgcolor="white",
        border_radius=14,
        text_size=14,
        content_padding=ft.Padding(left=15, top=5, right=15, bottom=5),
        on_submit=lambda e: procesar_codigo_barras(codigo_barras_input.value),
        on_focus=lambda e: campo_activo.update(control=codigo_barras_input),
        on_blur=lambda e: campo_activo.update(control=None) if campo_activo["control"] is codigo_barras_input else None,
    )

    usuario_codbarr_row = ft.Container(
        bgcolor="#EDF5FC",
        padding=10,
        border_radius=14,
        content=ft.Row(
            [
                ft.Container(expand=True),
                ft.Container(
                    codigo_barras_input,
                    width=300,
                    height=40,
                ),
                ft.Container(
                    nombre_producto_display,
                    width=300,
                    height=40,
                ),
                ft.Container(expand=True)
            ],
            spacing=10,
        ),
    )   

    def funcion_btn(texto, sub, bgcolor="#EDF5FC", color="black", expand=1, border_radius=14, on_click=None):
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
            border_radius=border_radius,
            on_click=on_click
        )

    botones_grid = ft.Column(
        [
            ft.Row(
                [
                    funcion_btn("+ Agregar", None, on_click=lambda e: agregar_cantidad()),
                    funcion_btn("- Quitar", None, on_click=lambda e: quitar_cantidad()),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    funcion_btn("Eliminar", None, on_click=lambda e: eliminar_producto()),
                    cantidad_display,
                ],
                spacing=6,
            ),
            ft.Row(
    [
        # Campo de monto recibido
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ATTACH_MONEY, size=20, color="#A9C2E8"),
                    monto_recibido_input,
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="white",
            border=border_all(1, "#cccccc"),
            padding=ft.Padding(left=10, top=5, right=10, bottom=5),
            expand=6,
            height=55,
            border_radius=14,
        ),
        funcion_btn("Cobrar", None, bgcolor="#4F7FE0", color="white", expand=1, on_click=activar_monto_recibido),
    ],
    spacing=6,
),
        ],
        spacing=6,
    )

    otros_botones = ft.Column(
        [
            ft.Row([
                funcion_btn("Nuevo", None, expand=1, on_click=lambda e: limpiar_ticket()),
                funcion_btn("Regresar", None, expand=1)
            ], spacing=6),
        ],
        spacing=6,
    )

    def numpad_btn(texto):
        async def al_presionar(e):
            boton = e.control
            # "Aprieta" el botón: lo encoge y oscurece un poco
            boton.scale = 0.88
            boton.bgcolor = "#D6E6FA"
            boton.update()

            digito_presionado(texto)

            # Pequeña pausa para que se note la animación y luego regresa a su estado normal
            await asyncio.sleep(0.08)
            boton.scale = 1
            boton.bgcolor = "#EDF5FC"
            boton.update()

        return ft.Container(
            content=ft.Text(texto, size=18, color="black"),
            bgcolor="#EDF5FC",
            border=border_all(1, "#cccccc"),
            alignment=ft.Alignment(0, 0),
            width=55,
            height=55,
            border_radius=8,
            ink=True,
            scale=1,
            animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT),  # anima el cambio de bgcolor
            on_click=al_presionar,
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
                email_box,
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
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=1,
        bgcolor="white",
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
    
    actualizar_ticket()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")