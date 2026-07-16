class Proveedor:
    def __init__(self, prov_nombre, prov_telefono, prov_calle, prov_num, prov_colonia, 
            prov_municipio, prov_estado, prov_codigoPostal, prov_correo, prov_tipo, prov_id = None):
        
        self.prov_id = prov_id
        self.prov_nombre = prov_nombre
        self.prov_telefono = prov_telefono
        self.prov_calle = prov_calle
        self.prov_num = prov_num
        self.prov_colonia = prov_colonia
        self.prov_municipio = prov_municipio
        self.prov_estado = prov_estado
        self.prov_codigoPostal = prov_codigoPostal
        self.prov_correo = prov_correo
        self.prov_tipo = prov_tipo

    def __str__(self):
        return f"Proveedor(prov_id = {self.prov_id}), nombre = '{self.prov_nombre}', telefono = '{self.prov_telefono}', calle = '{self.prov_calle}', numero = '{self.prov_num}', colonia = '{self.prov_colonia}', municipio = '{self.prov_municipio}', estado = '{self.prov_estado}', codigo postal = {self.prov_codigoPostal}, correo = '{self.prov_correo}', tipo = '{self.prov_tipo}'"
    
