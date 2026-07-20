from Productos.dao.producto_dao import ProductoDAO
from Productos.models.producto import Producto
from backend.dao.proveedor_dao import ProveedorDAO
from backend.models.proveedor import Proveedor


# FUNCIONES PROVEEDOR
def crear_proveedor():
    try:
        prov_nombre = input("Nombre del proveedor: ")
        prov_telefono = input("Telefono: ")
        prov_calle = input("Calle: ")
        prov_num = input("Num: ")
        prov_colonia = input("Colonia: ")
        prov_municipo = input("Municipio: ")
        prov_estado = input("Estado: ")
        prov_codigoPostal = int(input("Codigo Postal: "))
        prov_correo = input("Correo Electronico: ")
        prov_tipo = input("Tipo de proveedor: ")

        nuevo = Proveedor(prov_nombre, prov_telefono, prov_calle, prov_num, prov_colonia, prov_municipo, prov_estado, prov_codigoPostal, prov_correo, prov_tipo)
        ProveedorDAO.crear(nuevo)
        print("Proveedor creado con exito")

    except Exception as e:
        print("Error al crear un proveedor nuevo")
        print(e)

def ver_proveedores():
    try:

        proveedores = ProveedorDAO.obtener_todos()

        print("=========== Proveedores ===========")

        if len(proveedores) == 0:
            print("No hay proveedores registrados")
        else:
            for proveedor in proveedores:
                print("=============================================================================================")
                print(
                    f"ID: {proveedor.prov_id}, Nombre: {proveedor.prov_nombre}, Telefono: {proveedor.prov_telefono}, "
                    f"Calle: {proveedor.prov_calle}, Nuemro: {proveedor.prov_num}, "
                    f"Colonia: {proveedor.prov_colonia}, Municipio: {proveedor.prov_municipio}, "
                    f"Estado: {proveedor.prov_estado}, Codigo Postal: {proveedor.prov_codigoPostal}, "
                    f"Correo: {proveedor.prov_correo}, Tipo: {proveedor.prov_tipo}"
                )
                print("=============================================================================================")

    except Exception as e:
        print("Error al obtener proveedores")
        print(e)

def actualizar_proveedor():
    try:

        prov_id = int(input("ID del proveedor a actualizar: "))
        prov = ProveedorDAO.obtener_por_id(prov_id)

        if prov:

            prov.prov_nombre = input("Nuevo nombre del proveedor: ")
            prov.prov_telefono = input("Nuevo telefono: ")
            prov.prov_calle = input("Nueva calle: ")
            prov.prov_num = input("Nuevo num: ")
            prov.prov_colonia = input("Nueva colonia: ")
            prov.prov_municipo = input("Nuevo municipio: ")
            prov.prov_estado = input("Nuevo estado: ")
            prov.prov_codigoPostal = int(input("Nuevo codigo Postal: "))
            prov.prov_correo = input("Nuevo correo Electronico: ")
            prov.prov_tipo = input("Nuevo tipo de proveedor: ")

            ProveedorDAO.actualizar(prov)
            print("Proveedor actualizado con éxito")
        else:
            print("Proveedor no encontrado")

    except Exception as e:
        print("Error al actualizar proveedor")
        print(e)

def eliminar_proveedor():
    try:
        prov_id = int(input("ID del proveedor a eliminar: "))
        proveedor = ProveedorDAO.obtener_por_id(prov_id)

        if proveedor:
            ProveedorDAO.eliminar(prov_id)
            print("Proveedor eliminado con éxito")
        else:
            print("Proveedor no encontrado")

    except Exception as e:
        print("Error al eliminar proveedor")
        print(e)

def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver proveedores")
    print("2.- Crear proveedor")
    print("3.- Actualizar proveedor")
    print("4.- Eliminar proveedor")

    opc = int(input("Selecciona una opcion: "))

    match opc:
        case 1:
            ver_proveedores()
        case 2:
            crear_proveedor()
        case 3:
            actualizar_proveedor()
        case 4:
            eliminar_proveedor()

##========== PARTE DE OLIVER - PRODUCTOS - ==========

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