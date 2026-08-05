from backend.database.conexion import Conexion
from datetime import date


class CpmDAO:

    @staticmethod
    def generar_reporte(mes, anio):
        try:
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()

            sql_med = """
                SELECT dv.detalle_med_id, AVG(dv.detalle_cantidad) as promedio
                FROM detalle_ventas dv
                JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                WHERE dv.detalle_med_id IS NOT NULL
                AND EXTRACT(MONTH FROM v.venta_fecha) = %s
                AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                GROUP BY dv.detalle_med_id
            """
            cursor.execute(sql_med, (mes, anio))
            filas_med = cursor.fetchall()

            sql_prod = """
                SELECT dv.detalle_prod_id, AVG(dv.detalle_cantidad) as promedio
                FROM detalle_ventas dv
                JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                WHERE dv.detalle_prod_id IS NOT NULL
                AND EXTRACT(MONTH FROM v.venta_fecha) = %s
                AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                GROUP BY dv.detalle_prod_id
            """
            cursor.execute(sql_prod, (mes, anio))
            filas_prod = cursor.fetchall()

            sql_insertar_med = """
                INSERT INTO consumo_promedio_mensual
                (cpm_fecha, cpm_med_id, cpm_cantidad_promedio, cpm_mes, cpm_anio)
                VALUES (%s, %s, %s, %s, %s)
            """
            sql_insertar_prod = """
                INSERT INTO consumo_promedio_mensual
                (cpm_fecha, cpm_prod_id, cpm_cantidad_promedio, cpm_mes, cpm_anio)
                VALUES (%s, %s, %s, %s, %s)
            """

            for fila in filas_med:
                cursor.execute(sql_insertar_med, (date.today(), fila[0], fila[1], mes, anio))

            for fila in filas_prod:
                cursor.execute(sql_insertar_prod, (date.today(), fila[0], fila[1], mes, anio))

            conn.commit()
            cursor.close()
            print(f"Reporte generado correctamente para {mes}/{anio}")
            return True

        except Exception as e:
            conn.rollback()
            print("Error al generar reporte")
            print(e)
            return False

    @staticmethod
    def obtener_reporte(mes, anio):
        try:
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()

            # Reporte de medicamentos
            sql_med = """
                SELECT c.cpm_id, c.cpm_fecha, m.med_nombreGen, m.med_lab,
                       m.med_fraccion, c.cpm_cantidad_promedio
                FROM consumo_promedio_mensual c
                JOIN medicamentos m ON c.cpm_med_id = m.med_id
                WHERE c.cpm_mes = %s AND c.cpm_anio = %s
                AND c.cpm_med_id IS NOT NULL
                ORDER BY c.cpm_id ASC
            """
            cursor.execute(sql_med, (mes, anio))
            filas_med = cursor.fetchall()

            # Reporte de productos
            sql_prod = """
                SELECT c.cpm_id, c.cpm_fecha, p.prod_nombre, p.prod_marca,
                       p.prod_fraccion, c.cpm_cantidad_promedio
                FROM consumo_promedio_mensual c
                JOIN productos p ON c.cpm_prod_id = p.prod_id
                WHERE c.cpm_mes = %s AND c.cpm_anio = %s
                AND c.cpm_prod_id IS NOT NULL
                ORDER BY c.cpm_id ASC
            """
            cursor.execute(sql_prod, (mes, anio))
            filas_prod = cursor.fetchall()
            cursor.close()

            resultados = []
            for f in filas_med:
                resultados.append({
                    "cpm_id": f[0],
                    "cpm_fecha": f[1],
                    "nombre": f[2],
                    "laboratorio": f[3],
                    "fraccion": f[4],
                    "promedio": f[5]
                })
            for f in filas_prod:
                resultados.append({
                    "cpm_id": f[0],
                    "cpm_fecha": f[1],
                    "nombre": f[2],
                    "laboratorio": f[3],
                    "fraccion": f[4],
                    "promedio": f[5]
                })

            return resultados

        except Exception as e:
            print("Error al obtener reporte")
            print(e)
            return []