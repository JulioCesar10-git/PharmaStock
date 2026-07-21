class Medicamento:

    def __init__(self, med_codBarras, med_nombreGen, med_nombreComer, med_lab,
                 med_origen, med_concentracion, med_formaFarma, med_viaAdmi,
                 med_lote, med_fechaCad, med_fraccion, med_precio, med_existencia,
                 prov_id, med_id = None, cat_id = None):

        self.med_id = med_id
        self.cat_id = cat_id
        self.med_codBarras = med_codBarras
        self.med_nombreGen = med_nombreGen
        self.med_nombreComer = med_nombreComer
        self.med_lab = med_lab
        self.med_origen = med_origen
        self.med_concentracion = med_concentracion
        self.med_formaFarma = med_formaFarma
        self.med_viaAdmi = med_viaAdmi
        self.med_lote = med_lote
        self.med_fechaCad = med_fechaCad
        self.med_fraccion = med_fraccion
        self.med_precio = med_precio
        self.med_existencia = med_existencia
        self.prov_id = prov_id

    def __str__(self):
        return (f"Medicamento(id={self.med_id}, "
                f"nombre='{self.med_nombreGen}', "
                f"precio={self.med_precio}, "
                f"existencia={self.med_existencia})")