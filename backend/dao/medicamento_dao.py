from database.conexion import Conexion
from models.medicamento import Medicamento

class MedicamentoDAO:
    
    @staticmethod
    def crear(med):
        try:
            sql = """

                INSERT INTO medicamentos (med_codBarras, med_nombreGen, med_nombreComer,
                med_lab, med_origen, med_concentracion, med_formaFarma, med_viaAdmi,
                med_lote, med_fechaCad, med_fraccion, med_precio, med_existencia, prov_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING med_id

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (

                med.med_codBarras, med.med_nombreGen, med.med_nombreComer,
                med.med_lab, med.med_origen, med.med_concentracion,
                med.med_formaFarma, med.med_viaAdmi, med.med_lote,
                med.med_fechaCad, med.med_fraccion, med.med_precio,
                med.med_existencia, med.prov_id

            ))
            med.med_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return med
        
        except Exception as e:
            print("Error al crear medicamento")
            print(e)
            return None