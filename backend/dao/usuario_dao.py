import bcrypt
from backend.database.conexion import Conexion
from backend.models.usuario import Usuario

class UsuarioDAO:

    @staticmethod
    def login(usuario_correoElec, usuario_password):
        try:
            sql = """
                SELECT usuario_id, usuario_usuario, usuario_correoElec, 
                    usuario_password, usuario_cargo
                FROM usuarios WHERE usuario_correoElec = %s
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql, (usuario_correoElec,))
            fila = cursor.fetchone()
            cursor.close()

            if fila:
                password_bd = fila[3]
                if bcrypt.checkpw(usuario_password.encode("utf-8"), password_bd.encode("utf-8")):
                    return Usuario(
                        usuario_id=fila[0],
                        usuario_usuario=fila[1],
                        usuario_correoElec=fila[2],
                        usuario_password=fila[3],
                        usuario_cargo=fila[4],
                        usuario_telefono=None
                    )
            return None

        except Exception as e:
            print("Error al iniciar sesion")
            print(e)
            return None

    # ADMINISTRADOR REGISTRA UN USUARIO
    @staticmethod
    def registrar(usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo, usuario_apellidoPat=None, usuario_apellidoMat=None, usuario_telefono=None, usuario_imagen=None):
        try:
            password_encriptada = bcrypt.hashpw(usuario_password.encode("utf-8"), bcrypt.gensalt())

            sql = """
                INSERT INTO usuarios (usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo, usuario_apellidoPat, usuario_apellidoMat, usuario_telefono, usuario_imagen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql, (
                usuario_usuario,
                usuario_correoElec,
                password_encriptada.decode("utf-8"),
                usuario_cargo,
                usuario_apellidoPat,
                usuario_apellidoMat,
                usuario_telefono,
                usuario_imagen
            ))
            conn.commit()
            cursor.close()
            print("Usuario registrado con éxito")

        except Exception as e:
            print("Error al registrar usuario")
            print(e)

    #NUEVO AGREGADO
    @staticmethod
    def obtener_todos():
        try:
            sql = """
                SELECT usuario_id, usuario_usuario, usuario_correoElec, 
                    usuario_cargo, usuario_apellidoPat, usuario_apellidoMat,
                    usuario_telefono, usuario_imagen
                FROM usuarios
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql)
            filas = cursor.fetchall()
            cursor.close()
            return [Usuario(
                usuario_id=f[0],
                usuario_usuario=f[1],
                usuario_correoElec=f[2],
                usuario_password="",
                usuario_cargo=f[3],
                usuario_apellidoPat=f[4],
                usuario_apellidoMat=f[5],
                usuario_telefono=f[6],
                usuario_imagen=f[7]
            ) for f in filas]
        except Exception as e:
            print("Error al obtener usuarios")
            print(e)
            return []

    @staticmethod
    def eliminar(usuario_id):
        try:
            sql = "DELETE FROM usuarios WHERE usuario_id = %s"
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql, (usuario_id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Error al eliminar usuario")
            print(e)
            return False

    @staticmethod
    def actualizar(usuario):
        try:
            sql = """
                UPDATE usuarios
                SET usuario_usuario=%s, usuario_correoElec=%s, usuario_cargo=%s,
                    usuario_apellidoPat=%s, usuario_apellidoMat=%s, 
                    usuario_telefono=%s, usuario_imagen=%s
                WHERE usuario_id=%s
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql, (
                usuario.usuario_usuario,
                usuario.usuario_correoElec,
                usuario.usuario_cargo,
                usuario.usuario_apellidoPat,
                usuario.usuario_apellidoMat,
                usuario.usuario_telefono,
                usuario.usuario_imagen,
                usuario.usuario_id
            ))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Error al actualizar usuario")
            print(e)
            return False