class Venta:

    def __init__(self, venta_folio, venta_fecha, venta_usuario_id, venta_subtotal, venta_iva, venta_total, venta_id = None):

        self.venta_id = venta_id
        self.venta_folio = venta_folio
        self.venta_fecha = venta_fecha
        self.venta_usuario_id = venta_usuario_id
        self.venta_subtotal = venta_subtotal
        self.venta_total = venta_total
        self.venta_iva = venta_iva

    def __str__(self):
        return f"Venta(folio = {self.venta_folio}, fecha = {self.venta_fecha}, total = {self.venta_total})"

        