from datetime import datetime

ESTADO_FARMACIA = {
    "nombre": "Sin nombre asignado",
    "sucursal": "Sin sucursal asignada",
}

ESTADO_UI = {
    "modo_oscuro": False,
}

PRODUCTOS_GLOBALES = [
    # --- Medicamentos ---
    {
        "nombre": "Paracetamol 500mg",
        "tipo": "Medicamento",
        "categoria": "Analgésico",
        "precio": 45.0,
        "stock": 120,
        "caducidad": "03/2028",
        "alertas": [],
    },
    {
        "nombre": "Ibuprofeno 400mg",
        "tipo": "Medicamento",
        "categoria": "Antiinflamatorio",
        "precio": 58.5,
        "stock": 8,
        "caducidad": "11/2026",
        "alertas": [],
    },
    {
        "nombre": "Amoxicilina 500mg",
        "tipo": "Medicamento",
        "categoria": "Antibiótico",
        "precio": 89.0,
        "stock": 45,
        "caducidad": "07/2026",
        "alertas": [],
    },
    {
        "nombre": "Loratadina 10mg",
        "tipo": "Medicamento",
        "categoria": "Antialérgico",
        "precio": 62.0,
        "stock": 75,
        "caducidad": "05/2027",
        "alertas": [],
    },
    {
        "nombre": "Omeprazol 20mg",
        "tipo": "Medicamento",
        "categoria": "Antiácido",
        "precio": 71.0,
        "stock": 30,
        "caducidad": "09/2026",
        "alertas": [],
    },
    {
        "nombre": "Naproxeno 250mg",
        "tipo": "Medicamento",
        "categoria": "Analgésico",
        "precio": 55.0,
        "stock": 95,
        "caducidad": "01/2028",
        "alertas": [],
    },
    {
        "nombre": "Aspirina 500mg",
        "tipo": "Medicamento",
        "categoria": "Analgésico",
        "precio": 38.0,
        "stock": 150,
        "caducidad": "06/2027",
        "alertas": [],
    },
    {
        "nombre": "Ciprofloxacino 500mg",
        "tipo": "Medicamento",
        "categoria": "Antibiótico",
        "precio": 98.0,
        "stock": 20,
        "caducidad": "06/2026",
        "alertas": [],
    },
    {
        "nombre": "Losartán 50mg",
        "tipo": "Medicamento",
        "categoria": "Antihipertensivo",
        "precio": 110.0,
        "stock": 60,
        "caducidad": "02/2028",
        "alertas": [],
    },
    {
        "nombre": "Metformina 850mg",
        "tipo": "Medicamento",
        "categoria": "Antidiabético",
        "precio": 84.0,
        "stock": 40,
        "caducidad": "10/2026",
        "alertas": [],
    },
    {
        "nombre": "Salbutamol Inhalador",
        "tipo": "Medicamento",
        "categoria": "Broncodilatador",
        "precio": 145.0,
        "stock": 5,
        "caducidad": "08/2026",
        "alertas": [],
    },
    {
        "nombre": "Diclofenaco 100mg",
        "tipo": "Medicamento",
        "categoria": "Antiinflamatorio",
        "precio": 49.0,
        "stock": 88,
        "caducidad": "12/2027",
        "alertas": [],
    },
    # --- Productos (no medicamentos) ---
    {
        "nombre": "Suerox Sabor Uva",
        "tipo": "Producto",
        "categoria": "Rehidratante",
        "precio": 22.0,
        "stock": 200,
        "caducidad": "04/2027",
        "alertas": [],
    },
    {
        "nombre": "Electrolit Fresa-Kiwi",
        "tipo": "Producto",
        "categoria": "Rehidratante",
        "precio": 28.0,
        "stock": 15,
        "caducidad": "07/2026",
        "alertas": [],
    },
    {
        "nombre": "Vick VapoRub 50g",
        "tipo": "Producto",
        "categoria": "Cuidado personal",
        "precio": 65.0,
        "stock": 55,
        "caducidad": "05/2028",
        "alertas": [],
    },
    {
        "nombre": "Alka-Seltzer",
        "tipo": "Producto",
        "categoria": "Antiácido",
        "precio": 32.0,
        "stock": 70,
        "caducidad": "09/2026",
        "alertas": [],
    },
    {
        "nombre": "Listerine Original 500ml",
        "tipo": "Producto",
        "categoria": "Higiene bucal",
        "precio": 89.0,
        "stock": 42,
        "caducidad": "03/2029",
        "alertas": [],
    },
    {
        "nombre": "Colgate Total 12",
        "tipo": "Producto",
        "categoria": "Higiene bucal",
        "precio": 35.0,
        "stock": 130,
        "caducidad": "01/2029",
        "alertas": [],
    },
    {
        "nombre": "Centrum Adultos 30 Tabs",
        "tipo": "Producto",
        "categoria": "Vitaminas",
        "precio": 285.0,
        "stock": 18,
        "caducidad": "11/2027",
        "alertas": [],
    },
    {
        "nombre": "Redoxon Naranja 10 Tabs",
        "tipo": "Producto",
        "categoria": "Vitaminas",
        "precio": 95.0,
        "stock": 12,
        "caducidad": "08/2026",
        "alertas": [],
    },
    {
        "nombre": "Curitas Band-Aid 20pz",
        "tipo": "Producto",
        "categoria": "Primeros auxilios",
        "precio": 42.0,
        "stock": 90,
        "caducidad": "N/A",
        "alertas": [],
    },
    {
        "nombre": "Alcohol en Gel 70% 250ml",
        "tipo": "Producto",
        "categoria": "Higiene",
        "precio": 39.0,
        "stock": 3,
        "caducidad": "02/2028",
        "alertas": [],
    },
    {
        "nombre": "Termómetro Digital",
        "tipo": "Producto",
        "categoria": "Equipo médico",
        "precio": 120.0,
        "stock": 25,
        "caducidad": "N/A",
        "alertas": [],
    },
    {
        "nombre": "Cubrebocas Tricapa 50pz",
        "tipo": "Producto",
        "categoria": "Protección",
        "precio": 78.0,
        "stock": 65,
        "caducidad": "N/A",
        "alertas": [],
    },
]

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