from dao.producto_dao import ProductoDAO
from models.producto import Producto

# PRODUCTOS
def crear_producto():
    try:

        prod_codBarras = input("Codigo de barras: ")
        prod_nombre = input("Nombre del producto: ")
        prod_marca = input("Marca: ")
        prod_precio = float(input("Precio: "))
        prod_existencia = int(input("Existencia: "))
        prod_lote = input("Lote: ")
        prod_fechaCad = input("Fecha de caducidad: ")
        prod_fraccion = input("Fraccion: ")
        prov_id = int(input("ID del proveedor: "))

        nuevo = Producto(

            prod_codBarras, prod_nombre, prod_marca, prod_precio,
            prod_existencia, prod_lote, prod_fechaCad, prod_fraccion, prov_id

        )

        ProductoDAO.crear(nuevo)
        print("Producto creado con exito")

    except Exception as e:
        print("Error al crear el producto")
        print(e)


def ver_productos():
    try:

        productos = ProductoDAO.obtener_todos()

        print("=========== Productos disponibles ===========")

        if len(productos) == 0:
            print("No hay productos registrados.")
        else:
            for productos in productos:
                print("=============================================================================================")
                print(
                    f"ID: {productos.prod_id}, Código: {productos.prod_codBarras}, Nombre: {productos.prod_nombre}, "
                    f"Marca: {productos.prod_marca}, Precio: {productos.prod_precio}, "
                    f"Existencia: {productos.prod_existencia}, Lote: {productos.prod_lote}, "
                    f"Fecha de Caducidad: {productos.prod_fechaCad}, Fraccion: {productos.prod_fraccion}, "
                    f"Proveedor ID: {productos .prov_id}"
                )
                print("=============================================================================================")

    except Exception as e:
        print("Error al productos")
        print(e)

def buscar_producto():
    try:

        prod_id = int(input("ID del producto: "))

        productos = ProductoDAO.obtener_por_id(prod_id)

        if productos:
            print("=============================================================================================")
            print(
                    f"ID: {productos.prod_id}, Código: {productos.prod_codBarras}, Nombre: {productos.prod_nombre}, "
                    f"Marca: {productos.prod_marca}, Precio: {productos.prod_precio}, "
                    f"Existencia: {productos.prod_existencia}, Lote: {productos.prod_lote}, "
                    f"Fecha de Caducidad: {productos.prod_fechaCad}, Fraccion: {productos.prod_fraccion}, "
                    f"Proveedor ID: {productos.prov_id}"
                )
            print("=============================================================================================")
        else:
            print("Producto no encontrado")

    except Exception as e:
        print("Error al buscar producto")
        print(e)

def actualizar_producto():
    try:

        prod_id = int(input("ID del producto a actualizar: "))
        productos = ProductoDAO.obtener_por_id(prod_id)

        if productos:

            productos.prod_codBarras = input("Nuevo codigo de barras: ")
            productos.prod_nombre = input("Nuevo nombre del producto: ")
            productos.prod_marca = input("Nueva marca: ")
            productos.prod_precio = float(input("Nuevo precio: "))
            productos.prod_existencia = int(input("Nueva existencia: "))
            productos.prod_lote = input("Nuevo lote: ")
            productos.prod_fechaCad = input("Nueva fecha de caducidad: ")
            productos.prod_fraccion = input("Nueva fraccion: ")
            productos.prov_id = int(input("Nuevo ID del proveedor: "))

            ProductoDAO.actualizar(productos)
            print("Producto actualizado con éxito")
        else:
            print("Producto no encontrado")

    except Exception as e:
        print("Error al actualizar producto")
        print(e)

def eliminar_producto():
    try:
        prod_id = int(input("ID del producto a eliminar: "))
        productos = ProductoDAO.obtener_por_id(prod_id)

        if productos:
            ProductoDAO.eliminar(prod_id)
            print("Producto eliminado con éxito")
        else:
            print("Producto no encontrado")

    except Exception as e:
        print("Error al eliminar producto")
        print(e)

def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver productos")
    print("2.- Crear producto")
    print("3.- Actualizar producto")
    print("4.- Eliminar producto")
    
    opc = int(input("Selecciona una opcion: "))

    match opc:
        case 1:
            ver_productos()
        case 2:
            crear_producto()
        case 3:
            actualizar_producto()
        case 4:
            eliminar_producto()

if __name__ == "__main__":
    main()

