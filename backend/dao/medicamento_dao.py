from backend.database.conexion import Conexion
from backend.models.medicamento import Medicamento

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

    @staticmethod
    def obtener_todos():
        try:
            sql = """

                SELECT med_id, med_codBarras, med_nombreGen, med_nombreComer,
                med_lab, med_origen, med_concentracion, med_formaFarma, med_viaAdmi,
                med_lote, med_fechaCad, med_fraccion, med_precio, med_existencia, prov_id
                FROM medicamentos

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql)
            filas = cur.fetchall()
            cur.close()
            return [Medicamento(
                med_id=f[0], med_codBarras=f[1], med_nombreGen=f[2],
                med_nombreComer=f[3], med_lab=f[4], med_origen=f[5],
                med_concentracion=f[6], med_formaFarma=f[7], med_viaAdmi=f[8],
                med_lote=f[9], med_fechaCad=f[10], med_fraccion=f[11],
                med_precio=f[12], med_existencia=f[13], prov_id=f[14]
            ) for f in filas]
        
        except Exception as e:
            print("Error al obtener medicamentos")
            print(e)
            return []

    @staticmethod
    def obtener_por_id(med_id):
        try:
            sql = """

                SELECT med_id, med_codBarras, med_nombreGen, med_nombreComer,
                med_lab, med_origen, med_concentracion, med_formaFarma, med_viaAdmi,
                med_lote, med_fechaCad, med_fraccion, med_precio, med_existencia, prov_id
                FROM medicamentos WHERE med_id = %s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (med_id,))
            f = cur.fetchone()
            cur.close()
            if f:
                return Medicamento(
                    med_id=f[0], med_codBarras=f[1], med_nombreGen=f[2],
                    med_nombreComer=f[3], med_lab=f[4], med_origen=f[5],
                    med_concentracion=f[6], med_formaFarma=f[7], med_viaAdmi=f[8],
                    med_lote=f[9], med_fechaCad=f[10], med_fraccion=f[11],
                    med_precio=f[12], med_existencia=f[13], prov_id=f[14]
                )
            return None
        
        except Exception as e:
            print("Error al obtener medicamento")
            print(e)
            return None

    @staticmethod
    def actualizar(med):
        try:
            sql = """

                UPDATE medicamentos
                SET med_codBarras = %s, med_nombreGen = %s, med_nombreComer = %s,
                med_lab = %s, med_origen = %s, med_concentracion = %s, med_formaFarma = %s,
                med_viaAdmi = %s, med_lote = %s, med_fechaCad = %s, med_fraccion = %s,
                med_precio = %s, med_existencia = %s, prov_id = %s

                WHERE med_id=%s
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (

                med.med_codBarras, med.med_nombreGen, med.med_nombreComer,
                med.med_lab, med.med_origen, med.med_concentracion,
                med.med_formaFarma, med.med_viaAdmi, med.med_lote,
                med.med_fechaCad, med.med_fraccion, med.med_precio,
                med.med_existencia, med.prov_id, med.med_id

            ))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:

            print("Error al actualizar medicamento")
            print(e)
            return False
        
    @staticmethod
    def eliminar(med_id):
        try:
            sql = "DELETE FROM medicamentos WHERE med_id = %s"
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (med_id,))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:
            print("Error al eliminar medicamento")
            print(e)
            return False

