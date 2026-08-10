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

    @staticmethod
    def obtener_meses_con_ventas():
        """
        Devuelve los pares (anio, mes) para los que existen ventas
        registradas, ordenados del más reciente al más antiguo.
        Se usa para saber qué "reportes de ventas" mensuales existen.
        """
        try:
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()

            sql = """
                SELECT DISTINCT EXTRACT(YEAR FROM v.venta_fecha)::int AS anio,
                       EXTRACT(MONTH FROM v.venta_fecha)::int AS mes
                FROM ventas v
                ORDER BY anio DESC, mes DESC
            """
            cursor.execute(sql)
            filas = cursor.fetchall()
            cursor.close()
            return [{"anio": f[0], "mes": f[1]} for f in filas]

        except Exception as e:
            Conexion.obtener_conexion().rollback()
            print("Error al obtener meses con ventas")
            print(e)
            return []

    @staticmethod
    def generar_reporte_ventas(mes, anio):
        """
        Genera el resumen de VENTAS (en $) de un mes/año: total vendido,
        piezas de productos, piezas de medicamentos, detalle por artículo
        y proveedores involucrados.

        A diferencia de generar_reporte()/obtener_reporte() -que calculan
        el Consumo Promedio Mensual (CPM) usado para reabastecimiento y
        no manejan dinero- este método sí calcula el total en pesos,
        usando el precio actual de cada medicamento/producto (med_precio /
        prod_precio) multiplicado por las piezas vendidas en el mes.
        """
        vacio = {
            "productos": 0,
            "medicamentos": 0,
            "total": 0.0,
            "productos_lista": [],
            "proveedores_lista": [],
        }
        try:
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()

            sql_med = """
                SELECT m.med_id, m.med_nombreGen, m.med_precio, m.prov_id,
                       SUM(dv.detalle_cantidad) AS piezas
                FROM detalle_ventas dv
                JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                JOIN medicamentos m ON dv.detalle_med_id = m.med_id
                WHERE EXTRACT(MONTH FROM v.venta_fecha) = %s
                AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                GROUP BY m.med_id, m.med_nombreGen, m.med_precio, m.prov_id
            """
            cursor.execute(sql_med, (mes, anio))
            filas_med = cursor.fetchall()

            sql_prod = """
                SELECT p.prod_id, p.prod_nombre, p.prod_precio, p.prov_id,
                       SUM(dv.detalle_cantidad) AS piezas
                FROM detalle_ventas dv
                JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                JOIN productos p ON dv.detalle_prod_id = p.prod_id
                WHERE EXTRACT(MONTH FROM v.venta_fecha) = %s
                AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                GROUP BY p.prod_id, p.prod_nombre, p.prod_precio, p.prov_id
            """
            cursor.execute(sql_prod, (mes, anio))
            filas_prod = cursor.fetchall()

            sql_proveedores = """
                SELECT DISTINCT pr.prov_id, pr.prov_nombre, pr.prov_tipo
                FROM proveedores pr
                WHERE pr.prov_id IN (
                    SELECT m.prov_id FROM detalle_ventas dv
                    JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                    JOIN medicamentos m ON dv.detalle_med_id = m.med_id
                    WHERE EXTRACT(MONTH FROM v.venta_fecha) = %s
                    AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                    UNION
                    SELECT p.prov_id FROM detalle_ventas dv
                    JOIN ventas v ON dv.detalle_venta_id = v.venta_id
                    JOIN productos p ON dv.detalle_prod_id = p.prod_id
                    WHERE EXTRACT(MONTH FROM v.venta_fecha) = %s
                    AND EXTRACT(YEAR FROM v.venta_fecha) = %s
                )
            """
            cursor.execute(sql_proveedores, (mes, anio, mes, anio))
            filas_prov = cursor.fetchall()
            cursor.close()

            productos_lista = []
            medicamentos_piezas = 0
            productos_piezas = 0
            total = 0.0

            for f in filas_med:
                precio = float(f[2] or 0)
                piezas = int(f[4] or 0)
                medicamentos_piezas += piezas
                total += precio * piezas
                productos_lista.append({
                    "producto": {"nombre": f[1], "tipo": "Medicamento", "precio": precio},
                    "piezas": piezas,
                })

            for f in filas_prod:
                precio = float(f[2] or 0)
                piezas = int(f[4] or 0)
                productos_piezas += piezas
                total += precio * piezas
                productos_lista.append({
                    "producto": {"nombre": f[1], "tipo": "Producto", "precio": precio},
                    "piezas": piezas,
                })

            proveedores_lista = [{"nombre": f[1], "tipo": f[2]} for f in filas_prov]

            return {
                "productos": productos_piezas,
                "medicamentos": medicamentos_piezas,
                "total": round(total, 2),
                "productos_lista": productos_lista,
                "proveedores_lista": proveedores_lista,
            }

        except Exception as e:
            Conexion.obtener_conexion().rollback()
            print("Error al generar reporte de ventas")
            print(e)
            return vacio