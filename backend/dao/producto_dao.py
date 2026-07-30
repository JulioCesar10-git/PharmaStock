from backend.database.conexion import Conexion
from backend.models.producto import Producto

class ProductoDAO:

    @staticmethod
    def crear(prod):
        try:

            sql = """

                INSERT INTO productos (prod_codBarras, prod_nombre, prod_marca, prod_precio,
                prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id, cat_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING prod_id

            """

            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (

                prod.prod_codBarras, prod.prod_nombre, prod.prod_marca,
                prod.prod_precio, prod.prod_existencia, prod.prod_lote,
                prod.prod_fechaCad, prod.prod_fraccion, prod.prov_id, prod.cat_id

            ))
            prod.prod_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return prod
        
        except Exception as e:
            print("Error al crear producto")
            print(e)
            return None
    
    @staticmethod
    def obtener_todos():
        try:
            sql = """

                SELECT prod_id, prod_codBarras, prod_nombre, prod_marca, prod_precio,
                prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id, cat_id
                FROM productos

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql)
            filas = cur.fetchall()
            cur.close()
            return [Producto(
                prod_id=f[0], prod_codBarras=f[1], prod_nombre=f[2],
                prod_marca=f[3], prod_precio=f[4], prod_existencia=f[5],
                prod_lote=f[6], prod_fechaCad=f[7], prod_fraccion=f[8],
                prov_id=f[9], cat_id=f[10]
            ) for f in filas]
        
        except Exception as e:
            print("Error al obtener productos")
            print(e)
            return []
        
    @staticmethod
    def obtener_por_id(prod_id):
        try:
            sql = """

                SELECT prod_id, prod_codBarras, prod_nombre, prod_marca, prod_precio,
                prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id, cat_id
                FROM productos WHERE prod_id = %s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (prod_id,))
            f = cur.fetchone()
            cur.close()
            if f:
                return Producto(
                    prod_id=f[0], prod_codBarras=f[1], prod_nombre=f[2],
                    prod_marca=f[3], prod_precio=f[4], prod_existencia=f[5],
                    prod_lote=f[6], prod_fechaCad=f[7], prod_fraccion=f[8],
                    prov_id=f[9], cat_id=f[10]
                )
            return None
        
        except Exception as e:
            print("Error al obtener producto")
            print(e)
            return None

    @staticmethod
    def obtener_por_codigo_barras(codigo):
        try:
            sql = """

                SELECT prod_id, prod_codBarras, prod_nombre, prod_marca, prod_precio,
                prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id
                FROM productos WHERE prod_codBarras = %s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (codigo,))
            f = cur.fetchone()
            cur.close()
            if f:
                return Producto(
                    prod_id=f[0], prod_codBarras=f[1], prod_nombre=f[2],
                    prod_marca=f[3], prod_precio=f[4], prod_existencia=f[5],
                    prod_lote=f[6], prod_fechaCad=f[7], prod_fraccion=f[8],
                    prov_id=f[9]
                )
            return None
        
        except Exception as e:
            print("Error al buscar por código de barras")
            print(e)
            return None
        
    @staticmethod
    def actualizar(prod):
        try:
            sql = """

                UPDATE productos
                SET prod_codBarras = %s, prod_nombre = %s, prod_marca = %s,
                prod_precio = %s, prod_existencia = %s, prod_lote = %s, prod_fechaCad = %s,
                prod_fraccion = %s, prov_id = %s, cat_id = %s
                WHERE prod_id=%s

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (

                prod.prod_codBarras, prod.prod_nombre, prod.prod_marca,
                prod.prod_precio, prod.prod_existencia, prod.prod_lote,
                prod.prod_fechaCad, prod.prod_fraccion, prod.prov_id, prod.prod_id, prod.cat_id

            ))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:

            print("Error al actualizar producto")
            print(e)
            return False
        
    @staticmethod
    def eliminar(prod_id):
        try:
            sql = "DELETE FROM productos WHERE prod_id = %s"
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (prod_id,))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:
            print("Error al eliminar producto")
            print(e)
            return False
    
