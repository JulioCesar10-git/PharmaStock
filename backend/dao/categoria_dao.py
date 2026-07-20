from backend.database.conexion import Conexion
from backend.models.categoria import Categoria

class CategoriaDAO:

    @staticmethod
    def crear(categoria):
        try:

            sql = """

                INSERT INTO categorias(cat_nombre, cat_descripcion)
                VALUES (%s, %s)
                RETURNING cat_id

            """
            
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (categoria.cat_nombre, categoria.cat_descripcion))
            categoria.cat_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return categoria
        
        except Exception as e:
            print("Error al crear categoria")
            print(e)
            return None
        
    @staticmethod
    def obtener_todos():
        try:

            sql = "SELECT cat_id, cat_nombre, cat_descripcion FROM categorias"
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql)
            filas = cur.fetchall()
            cur.close()

            return [Categoria(cat_id=f[0], cat_nombre=f[1], cat_descripcion=f[2])
                    for f in filas]
    
        except Exception as e:
            print("Error al obtener categorias")
            print(e)
            return None
        
    @staticmethod 
    def obtener_por_id(cat_id):
        try:

            sql = "SELECT cat_id, cat_nombre, cat_descripcion FROM categorias WHRE id_categoria = %s"
            conn  = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (cat_id))
            f = cur.fetchone()
            cur.close()

            if f:
                return Categoria(cat_id=f[0], cat_nombre=f[1], cat_descripcion=f[2])
            return None
        
        except Exception as e:
            print("Error al obtener categoria")
            print(e)
            return None
    
    @staticmethod
    def actualizar(categoria):
        try:

            sql = """

                UPDATE categorias
                SET cat_nombre = %s, cat_descripcion = %s
                WHERE cat_id = %s

            """

            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (categoria.cat_nombre, categoria.cat_descripcion, categoria.cat_id))
            conn.commit()
            cur.close()
            return True
        
        except Exception as e:
            print("Error al actualizar categoria")
            print(e)
            return False
        
    @staticmethod
    def eliminar(cat_id):
        try:

            sql = "DELETE FROM categorias WHERE cat_id = %s"
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cur = conn.cursor()
            cur.execute(sql, (cat_id))
            conn.commit()
            cur.close
            return True
        
        except Exception as e:
            print("Error al eliminar categoria")
            print(e)
            return False