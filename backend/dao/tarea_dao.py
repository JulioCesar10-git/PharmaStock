from backend.database.conexion import Conexion
from backend.models.tarea import Tarea

class TareaDAO:
    
    @staticmethod
    def crear(tarea: Tarea):
        try:

            sql = """

                INSERT INTO tareas (tarea_asunto)
                VALUES (%s)
                RETURNING tarea_id

            """

            conn = Conexion.obtener_conexion()
            cur = conn.cursor()
            cur.execute(sql, (
                tarea.tarea_asunto,
            ))
            tarea.tarea_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return tarea

        except Exception as e:
            print("Error al crear una tarea")
            print(e)
            return None

    @staticmethod
    def obtener_todos():
        try:
            sql = """
                SELECT tarea_id, tarea_asunto
                FROM tareas
                ORDER BY tarea_id
            """

            conn = Conexion.obtener_conexion()
            cur = conn.cursor()
            cur.execute(sql)

            registros = cur.fetchall()

            tareas = []

            for registro in registros:
                tarea = Tarea(
                    tarea_asunto=registro[1],
                    tarea_id=registro[0]
                )
                tareas.append(tarea)

            cur.close()

            return tareas

        except Exception as e:
            print("Error al obtener las tareas")
            print(e)
            return []

    @staticmethod
    def obtener_por_id(tarea_id):
        try:
            sql = """
                SELECT tarea_id, tarea_asunto
                FROM tareas
                WHERE tarea_id = %s
            """

            conn = Conexion.obtener_conexion()
            cur = conn.cursor()
            cur.execute(sql, (tarea_id,))

            registro = cur.fetchone()

            cur.close()

            if registro:
                return Tarea(
                    tarea_asunto=registro[1],
                    tarea_id=registro[0]
                )

            return None

        except Exception as e:
            print("Error al obtener la tarea")
            print(e)
            return None

    @staticmethod
    def eliminar(tarea_id):
        try:
            sql = """
                DELETE FROM tareas
                WHERE tarea_id = %s
            """

            conn = Conexion.obtener_conexion()
            cur = conn.cursor()

            cur.execute(sql, (tarea_id,))
            conn.commit()

            filas_afectadas = cur.rowcount

            cur.close()

            return filas_afectadas > 0

        except Exception as e:
            print("Error al eliminar la tarea")
            print(e)
            return False