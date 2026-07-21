from backend.database.conexion import Conexion
from backend.models.venta import Venta

class VentaDAO:

    @staticmethod
    def crear_venta(venta: Venta, carrito: list):
        try:
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()

            sql_venta = """

                INSERT INTO ventas (venta_folio, venta_usuario_id, venta_subtotal, venta_iva, venta_total)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING venta_id

            """
            cursor.execute(sql_venta, (
                venta.venta_folio,
                venta.venta_usuario_id,
                venta.venta_subtotal,
                venta.venta_iva,
                venta.venta_total
            ))
            venta_id = cursor.fetchone()[0]

            for item in carrito:

                sql_detalle = """

                    INSERT INTO detalle_ventas (detalle_venta_id, detalle_producto_id,
                    detalle_cantidad, detalle_precio_unitario, detalle_subtotal)
                    VALUES (%s, %s, %s, %s, %s)

                """
                cursor.execute(sql_detalle, (
                    venta_id,
                    item["producto_id"],
                    item["cantidad"],
                    item["precio_unitario"],
                    item["subtotal"]
                ))

                # DESCONTAR STOCK
                if item["tipo"] == "med":

                    sql_stock = """

                        UPDATE medicamentos
                        SET med_existencia = med_existencia - %s
                        WHERE med_id = %s

                    """
                else:

                    sql_stock = """

                        UPDATE productos
                        SET prod_existencia = prod_existencia - %s
                        WHERE producto_id = %s

                    """
                cursor.execute(sql_stock, (item["cantidad"], item["producto_id"]))

            conn.commit()
            cursor.close()
            print(f"Venta registrada con éxito, folio: {venta.venta_folio}")
            return venta_id

        except Exception as e:
            conn.rollback()
            print("Error al registrar la venta")
            print(e)
            return None
        
    @staticmethod
    def corte_de_caja():
        try:
            sql = """
                SELECT COUNT(*), COALESCE(SUM(venta_total), 0)
                FROM ventas
                WHERE DATE(venta_fecha) = CURRENT_DATE
            """
            conn = Conexion.obtener_conexion()
            conn.rollback()
            cursor = conn.cursor()
            cursor.execute(sql)
            resultado = cursor.fetchone()
            cursor.close()

            return {
                "total_ventas": resultado[0],
                "total_dinero": resultado[1]
            }

        except Exception as e:
            print("Error al generar corte de caja")
            print(e)
            return None