class DetalleVenta:

    def _init_(self, detalle_venta_id, detalle_producto_id, detalle_cantidad, detalle_precio_unitario, detalle_subtotal, detalle_id=None):
        
        self.detalle_id = detalle_id
        self.detalle_venta_id = detalle_venta_id
        self.detalle_producto_id = detalle_producto_id
        self.detalle_cantidad = detalle_cantidad
        self.detalle_precio_unitario = detalle_precio_unitario
        self.detalle_subtotal = detalle_subtotal

    def _str_(self):
        return f"DetalleVenta(producto_id={self.detalle_producto_id}, cantidad={self.detalle_cantidad}, subtotal={self.detalle_subtotal})"