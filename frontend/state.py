from datetime import datetime

from backend.dao.medicamento_dao import MedicamentoDAO
from backend.dao.producto_dao import ProductoDAO

ESTADO_FARMACIA = {
    "nombre": "Sin nombre asignado",
    "sucursal": "Sin sucursal asignada",
}

ESTADO_UI = {
    "modo_oscuro": False,
}

def _fecha_cad_a_texto(fecha_cad):
    """Convierte una fecha de la BD (date/datetime) al formato 'MM/AAAA'
    que usa obtener_estado_caducidad(). Si no hay fecha, devuelve 'N/A'."""
    if not fecha_cad:
        return "N/A"
    return fecha_cad.strftime("%m/%Y")


def _producto_desde_medicamento(med):
    nombre = med.med_nombreComer or med.med_nombreGen or "Medicamento sin nombre"
    if med.med_concentracion and med.med_concentracion not in nombre:
        nombre = f"{nombre} {med.med_concentracion}".strip()

    return {
        "nombre": nombre,
        "tipo": "Medicamento",
        "categoria": "Sin categoría",  # TODO: resolver cat_id a nombre real cuando haya DAO de categorías
        "precio": float(med.med_precio) if med.med_precio is not None else 0.0,
        "stock": med.med_existencia if med.med_existencia is not None else 0,
        "caducidad": _fecha_cad_a_texto(med.med_fechaCad),
        "alertas": [],
    }


def _producto_desde_producto(prod):
    return {
        "nombre": prod.prod_nombre or "Producto sin nombre",
        "tipo": "Producto",
        "categoria": "Sin categoría",  # TODO: resolver cat_id a nombre real cuando haya DAO de categorías
        "precio": float(prod.prod_precio) if prod.prod_precio is not None else 0.0,
        "stock": prod.prod_existencia if prod.prod_existencia is not None else 0,
        "caducidad": _fecha_cad_a_texto(prod.prod_fechaCad),
        "alertas": [],
    }


PRODUCTOS_GLOBALES = []


# --- Recarga PRODUCTOS_GLOBALES desde la BD (medicamentos + productos).
#     Se muta la misma lista en su lugar (clear + extend) para que los
#     módulos que ya hicieron "from frontend.state import PRODUCTOS_GLOBALES"
#     vean los datos actualizados sin tener que reimportar nada. ---
def cargar_productos_desde_bd():
    nuevos = []

    for med in MedicamentoDAO.obtener_todos():
        nuevos.append(_producto_desde_medicamento(med))

    for prod in ProductoDAO.obtener_todos():
        nuevos.append(_producto_desde_producto(prod))

    PRODUCTOS_GLOBALES.clear()
    PRODUCTOS_GLOBALES.extend(nuevos)
    return PRODUCTOS_GLOBALES


cargar_productos_desde_bd()

_PROVEEDORES_BASE = [
    ("Birmex", "Medicamentos", 50, "+52", "224-568-254"),
    ("Roche México", "Medicamentos", 32, "+52", "244-525-126"),
    ("Genomma Lab", "Productos", 100, "+35", "356-595-639"),
    ("Grupo PiSA", "Medicamentos", 35, "+32", "321-465-465"),
    ("Genéricos México", "Medicamentos", 35, "+52", "246-569-569"),
    ("Farmacéutica Senosiain", "Medicamentos", 60, "+52", "228-441-903"),
    ("Landsteiner Scientific", "Productos", 45, "+1", "305-772-810"),
    ("Sanofi México", "Medicamentos", 80, "+52", "551-234-908"),
]

PROVEEDORES_GLOBALES = []
for _i, (_nombre, _tipo, _productos, _lada, _numero) in enumerate(_PROVEEDORES_BASE):
    PROVEEDORES_GLOBALES.append({
        "no": _i + 1,
        "nombre": _nombre,
        "tipo": _tipo,
        "productos": _productos,
        "contacto": f"({_lada}){_numero}",
    })

def _parsear_mmaaaa(caducidad):
    """Acepta 'MM/AAAA' (formato correcto) y, por compatibilidad con datos
    guardados con año de 2 dígitos ('MM/AA'), también ese formato.
    Devuelve un datetime o None si no se pudo interpretar."""
    for fmt in ("%m/%Y", "%m/%y"):
        try:
            return datetime.strptime(caducidad, fmt)
        except ValueError:
            continue
    return None


def obtener_estado_caducidad(caducidad):
    if not caducidad or caducidad == "N/A":
        return None
    fecha_cad = _parsear_mmaaaa(caducidad)
    if fecha_cad is None:
        return None
    hoy = datetime.now()
    diferencia_meses = (fecha_cad.year - hoy.year) * 12 + (fecha_cad.month - hoy.month)
    if diferencia_meses < 0:
        return "Caducado"
    elif 0 <= diferencia_meses <= 3:
        return "Por caducar"
    return None