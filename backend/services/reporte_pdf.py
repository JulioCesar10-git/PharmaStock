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