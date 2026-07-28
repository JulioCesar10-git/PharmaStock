import bcrypt
from backend.database.conexion import Conexion
from backend.models.usuario import Usuario

class UsuarioDAO:

    @staticmethod
    def login(usuario_correoElec, usuario_password):
        try:
            sql = """

            SELECT usuario_id, usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo FROM usuarios WHERE usuario_correoElec = %s

            """

            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(sql, (usuario_correoElec,))
            fila = cursor.fetchone()
            cursor.close()

            if fila:
                password_bd = fila[3]
                if bcrypt.checkpw(usuario_password.encode("utf-8"), password_bd.encode("utf-8")):
                    return Usuario(usuario_id = fila[0], usuario_usuario = fila[1], usuario_correoElec = fila[2], usuario_password = fila[3], usuario_cargo = fila[4])
            return None
    
            
        except Exception as e:
            print("Error al iniciar sesion")
            print(e)
            return None

# ADMINISTRADOR REGISTRA UN USUARIO
    @staticmethod
    def registrar(usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo):
        try:
            password_encriptada = bcrypt.hashpw(usuario_password.encode("utf-8"), bcrypt.gensalt())

            sql = """

            INSERT INTO usuarios (usuario_usuario, usuario_correoElec, usuario_password, usuario_cargo)
            VALUES
            (%s, %s, %s, %s)

            """
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(sql, (
                usuario_usuario,
                usuario_correoElec,
                password_encriptada.decode("utf-8"),
                usuario_cargo
            ))
            conn.commit()
            cursor.close()
            print("Usuario registrado con exito")
        
        except Exception as e:
            print("Error al registrar usuario")
            print(e)