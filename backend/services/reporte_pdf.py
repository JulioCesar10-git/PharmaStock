from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from backend.dao.cpm_dao import CpmDAO
from backend.dao.venta_dao import VentaDAO
import os

def _construir_tabla(filas):
    tabla = Table(filas, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2255D8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FF")]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla

def generar_reporte_medicamentos_pdf(mes, anio):
    datos = VentaDAO.reporte_mensual_medicamentos(mes, anio)

    if not datos:
        print("No hay datos de medicamentos para generar el reporte")
        return

    os.makedirs("reportes", exist_ok = True)
    nombre_archivo = f"reportes/reporte_medicamentos_{mes}_{anio}.pdf"

    doc = SimpleDocTemplate(nombre_archivo, pagesize = A4)
    estilos = getSampleStyleSheet()
    contenido = []

    contenido.append(Paragraph(f"Reporte Mensual de Medicamentos - {mes}/{anio}", estilos["Title"]))
    contenido.append(Spacer(1, 20))

    encabezados = ["Fecha", "Venta ID", "Med ID", "Nombre Genérico", "Laboratorio", "Fracción", "Cantidad"]
    filas = [encabezados]

    for d in datos:
        filas.append([
            str(d["fecha"]),
            str(d["venta_id"]),
            str(d["med_id"]),
            d["nombre"],
            d["laboratorio"],
            d["fraccion"],
            str(d["cantidad"])
        ])

    contenido.append(_construir_tabla(filas))
    doc.build(contenido)
    print(f"PDF generado: {nombre_archivo}")

def generar_reporte_productos_pdf(mes, anio):
    datos = VentaDAO.reporte_mensual_productos(mes, anio)

    if not datos:
        print("No hay datos de productos para generar el reporte")
        return

    os.makedirs("reportes", exist_ok=True)
    nombre_archivo = f"reportes/reporte_productos_{mes}_{anio}.pdf"

    doc = SimpleDocTemplate(nombre_archivo, pagesize = A4)
    estilos = getSampleStyleSheet()
    contenido = []

    contenido.append(Paragraph(f"Reporte Mensual de Productos - {mes}/{anio}", estilos["Title"]))
    contenido.append(Spacer(1, 20))

    encabezados = ["Fecha", "Venta ID", "Producto ID", "Nombre", "Marca", "Fracción", "Cantidad"]
    filas = [encabezados]

    for d in datos:
        filas.append([
            str(d["fecha"]),
            str(d["venta_id"]),
            str(d["producto_id"]),
            d["nombre"],
            d["marca"],
            d["fraccion"],
            str(d["cantidad"])
        ])

    contenido.append(_construir_tabla(filas))
    doc.build(contenido)
    print(f"PDF generado: {nombre_archivo}")

def generar_reporte_ventas_pdf(mes, anio):
    """
    Genera el PDF del reporte de VENTAS de un mes (el que se ve en la
    pantalla de Reportes: total en $, piezas de productos/medicamentos,
    detalle por artículo y proveedores involucrados).

    Usa CpmDAO.generar_reporte_ventas(), que calcula el total en $ a
    partir de ventas/detalle_ventas (a diferencia de
    CpmDAO.obtener_reporte(), que es el CPM de reabastecimiento).

    Devuelve la ruta del PDF generado, o None si no hay datos.
    """
    resumen = CpmDAO.generar_reporte_ventas(mes, anio)
    productos_lista = resumen.get("productos_lista", [])
    proveedores_lista = resumen.get("proveedores_lista", [])

    if not productos_lista:
        print("No hay datos de ventas para generar el reporte")
        return None

    os.makedirs("reportes", exist_ok=True)
    nombre_archivo = f"reportes/reporte_ventas_{mes}_{anio}.pdf"

    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4)
    estilos = getSampleStyleSheet()
    contenido = []

    contenido.append(Paragraph(f"Reporte de Ventas - {mes}/{anio}", estilos["Title"]))
    contenido.append(Spacer(1, 12))

    resumen_txt = (
        f"Piezas de productos: {resumen['productos']}  |  "
        f"Piezas de medicamentos: {resumen['medicamentos']}  |  "
        f"Total: ${resumen['total']:.2f}"
    )
    contenido.append(Paragraph(resumen_txt, estilos["Normal"]))
    contenido.append(Spacer(1, 18))

    contenido.append(Paragraph("Productos y medicamentos vendidos", estilos["Heading2"]))
    contenido.append(Spacer(1, 6))
    encabezados_prod = ["Tipo", "Nombre", "Piezas", "Precio unitario", "Subtotal"]
    filas_prod = [encabezados_prod]
    for item in productos_lista:
        prod = item.get("producto", {})
        precio = float(prod.get("precio", 0.0) or 0.0)
        piezas = int(item.get("piezas", 0) or 0)
        filas_prod.append([
            prod.get("tipo", ""),
            prod.get("nombre", ""),
            str(piezas),
            f"${precio:.2f}",
            f"${precio * piezas:.2f}",
        ])
    contenido.append(_construir_tabla(filas_prod))

    if proveedores_lista:
        contenido.append(Spacer(1, 20))
        contenido.append(Paragraph("Proveedores involucrados", estilos["Heading2"]))
        contenido.append(Spacer(1, 6))
        encabezados_prov = ["Nombre", "Tipo"]
        filas_prov = [encabezados_prov]
        for prov in proveedores_lista:
            filas_prov.append([prov.get("nombre", ""), prov.get("tipo", "")])
        contenido.append(_construir_tabla(filas_prov))

    doc.build(contenido)
    print(f"PDF generado: {nombre_archivo}")
    return nombre_archivo

def generar_reporte_cpm_pdf(mes, anio):
    datos = CpmDAO.obtener_reporte(mes, anio)

    if not datos:
        print("No hay datos para generar el reporte CPM")
        return

    os.makedirs("reportes", exist_ok=True)
    nombre_archivo = f"reportes/reporte_cpm_{mes}_{anio}.pdf"

    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4)
    estilos = getSampleStyleSheet()
    contenido = []

    contenido.append(Paragraph(f"Reporte de Consumo Promedio Mensual - {mes}/{anio}", estilos["Title"]))
    contenido.append(Spacer(1, 20))

    encabezados = ["CPM ID", "Fecha", "Nombre Genérico", "Laboratorio", "Fracción", "Cantidad Promedio"]
    filas = [encabezados]

    for d in datos:
        filas.append([
            str(d["cpm_id"]),
            str(d["cpm_fecha"]),
            d["nombre"],
            d["laboratorio"],
            d["fraccion"],
            str(round(d["promedio"], 2))
        ])

    contenido.append(_construir_tabla(filas))
    doc.build(contenido)
    print(f"PDF generado: {nombre_archivo}")