from backend.database.conexion import Conexion
from datetime import date


class CpmDAO:

    @staticmethod
    def generar_reporte(mes, anio):
        try:
            sql_calcular = """

                SELECT
                    dv.detalle_producto_id,
                    AVG(dv.detalle_cantidad) as promedio
                FROM detalle_ventas dv
                JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                WHERE EXTRACT(MONTH FROM v.venta_fecha) = %s
                AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                GROUP BY dv.detalle_producto_id

            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql_calcular, (mes, anio))
            filas = cursor.fetchall()

            sql_insertar = """

                INSERT INTO consumo_promedio_mensual
                (cpm_fecha, cpm_prod_id, cpm_cantidad_promedio, cpm_mes, cpm_anio)
                VALUES (%s, %s, %s, %s, %s)

            """
            for fila in filas:
                cursor.execute(sql_insertar, (
                    date.today(),
                    fila[0],
                    fila[1],
                    mes,
                    anio
                ))

            conn.commit()
            cursor.close()
            print(f"Reporte generado correctamente para {mes}/{anio}")
            return True

        except Exception as e:
            conn.rollback()
            print("Error al generar reporte")
            print(e)
            return False