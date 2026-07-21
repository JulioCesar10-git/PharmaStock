class Producto:

    def __init__(self, prod_codBarras, prod_nombre, prod_marca, prod_precio, prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id, prod_id = None):
        
        self.prod_id = prod_id
        self.prod_codBarras = prod_codBarras
        self.prod_nombre = prod_nombre
        self.prod_marca = prod_marca
        self.prod_precio = prod_precio
        self.prod_existencia = prod_existencia
        self.prod_lote = prod_lote
        self.prod_fechaCad = prod_fechaCad
        self.prod_fraccion = prod_fraccion
        self.prov_id = prov_id

    def __str__(self):

        return (f"Producto(id = {self.prod_id}), Nombre = '{self.prod_nombre}', Precio = {self.prod_precio}, Existencia = {self.prod_existencia}")
