from frontend.state import PRODUCTOS_GLOBALES, obtener_estado_caducidad

def _tiene_stock_bajo(producto):
    alertas = producto.get("alertas", [])
    if isinstance(alertas, list) and any("stock bajo" in str(a).lower() for a in alertas):
        return True

    stock_raw = producto.get("stock", 0)
    if isinstance(stock_raw, str):
        numeros_str = "".join(filter(str.isdigit, stock_raw))
        stock_num = int(numeros_str) if numeros_str else 999
    else:
        stock_num = int(stock_raw) if stock_raw is not None else 999

    return stock_num <= 50

def _tiene_aviso_caducidad(producto):
    estado = obtener_estado_caducidad(producto.get("caducidad"))
    return estado in ("Por caducar", "Caducado")

def contar_avisos_inventario(productos=None):
    lista = productos if productos is not None else PRODUCTOS_GLOBALES
    return sum(
        1 for p in lista
        if _tiene_stock_bajo(p) or _tiene_aviso_caducidad(p)
    )

# --- Genera la misma lista de avisos que muestra la tarjeta "AVISOS Y ALERTAS"
#     de la pestaña General (components/avisos.py), para reutilizarla en
#     cualquier otra parte de la app (p. ej. el Centro de Notificaciones) ---
def obtener_avisos_inventario(productos=None):
    lista = productos if productos is not None else PRODUCTOS_GLOBALES
    avisos = []

    for prod in lista:
        nombre = prod.get("nombre", "Producto")
        stock = prod.get("stock", 0)
        caducidad = prod.get("caducidad", "N/A")

        if stock <= 50:
            avisos.append({"nombre": nombre, "tipo": "Stock bajo", "detalle": f"Stock: {stock} pz"})

        estado_cad = obtener_estado_caducidad(caducidad)
        if estado_cad == "Caducado":
            avisos.append({"nombre": nombre, "tipo": "Caducado", "detalle": f"Cad: {caducidad}"})
        elif estado_cad == "Por caducar":
            avisos.append({"nombre": nombre, "tipo": "Por caducar", "detalle": f"Cad: {caducidad}"})

    return avisos