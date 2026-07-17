from backend.database.conexion import Conexion
from backend.models.proveedor import Proveedor

class ProveedorDAO:

    @staticmethod
    def crear(proveedor: Proveedor):

        sql = """

            INSERT INTO proveedores (prov_nombre, prov_telefono, prov_calle, prov_num, prov_colonia, prov_municipio, prov_estado, prov_codigoPostal, prov_correo, prov_tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING prov_id

        """

        conn = Conexion.obtener_conexion()
        cur = conn.cursor()
        cur.execute(sql, (
            proveedor.prov_nombre,
            proveedor.prov_telefono,
            proveedor.prov_calle,
            proveedor.prov_num,
            proveedor.prov_colonia,
            proveedor.prov_municipio,
            proveedor.prov_estado,
            proveedor.prov_codigoPostal,
            proveedor.prov_correo,
            proveedor.prov_tipo
        ))
        proveedor.prov_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return proveedor

    @staticmethod
    def obtener_todos():
        try:
            sql = """

                SELECT prov_id, prov_nombre, prov_telefono, prov_calle, prov_num,
                prov_colonia, prov_municipio, prov_estado, prov_codigoPostal, prov_correo,
                prov_tipo
                FROM proveedores

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql)
            filas = cur.fetchall()
            cur.close()
            return [Proveedor(
                prov_id=f[0], prov_nombre=f[1], prov_telefono=f[2],
                prov_calle=f[3], prov_num=f[4], prov_colonia=f[5],
                prov_municipio=f[6], prov_estado=f[7], prov_codigoPostal=f[8],
                prov_correo=f[9], prov_tipo=f[10]
            ) for f in filas]
        
        except Exception as e:
            print("Error al obtener proveedores")
            print(e)
            return []

    @staticmethod
    def obtener_por_id(prov_id):
        try:
            sql = """

                SELECT prov_id, prov_nombre, prov_telefono, prov_calle, prov_num,
                prov_colonia, prov_municipio, prov_estado, prov_codigoPostal, prov_correo, prov_tipo
                FROM proveedores WHERE prov_id = %s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (prov_id,))
            f = cur.fetchone()
            cur.close()
            if f:
                return Proveedor(
                    prov_id=f[0], prov_nombre=f[1], prov_telefono=f[2],
                    prov_calle=f[3], prov_num=f[4], prov_colonia=f[5],
                    prov_municipio=f[6], prov_estado=f[7], prov_codigoPostal=f[8],
                    prov_correo=f[9], prov_tipo=f[10]
                )
            return None
        
        except Exception as e:
            print("Error al obtener proveedor")
            print(e)
            return None      

    @staticmethod
    def actualizar(prov):
        try:
            sql = """

                UPDATE proveedores
                SET prov_nombre = %s, prov_telefono = %s, prov_calle = %s,
                prov_num = %s, prov_colonia = %s, prov_municipio = %s, prov_estado = %s,
                prov_codigoPostal = %s, prov_correo = %s, prov_tipo = %s

                WHERE prov_id = %s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (

                prov.prov_nombre, prov.prov_telefono, prov.prov_calle,
                prov.prov_num, prov.prov_colonia, prov.prov_municipio,
                prov.prov_estado, prov.prov_codigoPostal, prov.prov_correo, prov.prov_tipo, prov.prov_id

            ))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:

            print("Error al actualizar proveedor")
            print(e)
            return False    
