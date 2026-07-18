class Categoria:
    def __init__(self, cat_nombre, cat_descripcion, cat_id =  None):

        self.cat_id = cat_id
        self.cat_nombre = cat_nombre
        self.cat_descripcion = cat_descripcion

    def __str__(self):
        return f"Categoria(id = {self.cat_id}, nombre = '{self.cat_nombre}', descripcion = '{self.cat_descripcion}')"
    