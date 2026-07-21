# IMPORT´S
from backend.dao.proveedor_dao import ProveedorDAO
from backend.models.proveedor import Proveedor

from backend.dao.medicamento_dao import MedicamentoDAO
from backend.models.medicamento import Medicamento

from backend.dao.producto_dao import ProductoDAO
from backend.models.producto import Producto

from backend.dao.categoria_dao import CategoriaDAO
from backend.models.categoria import Categoria

# FUNCIONES DE PROVEEDOR
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

# FUNCIONES DE MEDICAMENTOS
def crear_medicamento():
    try:

        med_codBarras = input("Código de barras: ")
        med_nombreGen = input("Nombre genérico: ")
        med_nombreComer = input("Nombre comercial: ")
        med_lab = input("Laboratorio: ")
        med_origen = input("Origen: ")
        med_concentracion = input("Concentración: ")
        med_formaFarma = input("Forma farmacéutica: ")
        med_viaAdmi = input("Vía de administración: ")
        med_lote = input("Lote: ")
        med_fechaCad = input("Fecha de caducidad (YYYY-MM-DD): ")
        med_fraccion = input("Fracción: ")
        med_precio = float(input("Precio: "))
        med_existencia = int(input("Existencia: "))
        prov_id = int(input("ID del proveedor: "))

        nuevo = Medicamento(
            med_codBarras, med_nombreGen, med_nombreComer, med_lab,
            med_origen, med_concentracion, med_formaFarma, med_viaAdmi,
            med_lote, med_fechaCad, med_fraccion, med_precio, med_existencia, prov_id
        )
        MedicamentoDAO.crear(nuevo)
        print("Medicamento creado con éxito")

    except Exception as e:
        print("Error al crear medicamento")
        print(e)

def ver_medicamentos():
    try:

        medicamentos = MedicamentoDAO.obtener_todos()

        print("=========== Medicamentos disponibles ===========")

        if len(medicamentos) == 0:
            print("No hay medicamentos registrados.")
        else:
            for m in medicamentos:
                print("=======================================================================================")
                print(
                    f"ID: {m.med_id}, Código: {m.med_codBarras}, Nombre genérico: {m.med_nombreGen}, "
                    f"Nombre comercial: {m.med_nombreComer}, Laboratorio: {m.med_lab}, "
                    f"Origen: {m.med_origen}, Concentración: {m.med_concentracion}, "
                    f"Forma farmacéutica: {m.med_formaFarma}, Vía: {m.med_viaAdmi}, "
                    f"Lote: {m.med_lote}, Caducidad: {m.med_fechaCad}, "
                    f"Fracción: {m.med_fraccion}, Precio: ${m.med_precio}, "
                    f"Existencia: {m.med_existencia}, Proveedor ID: {m.prov_id}"
                )
                print("=======================================================================================")

    except Exception as e:
        print("Error al obtener medicamentos")
        print(e)

def buscar_medicamento():
    try:

        med_id = int(input("ID del medicamento: "))

        m = MedicamentoDAO.obtener_por_id(med_id)

        if m:
            print("=======================================================================================")
            print(
                f"ID: {m.med_id}, Código: {m.med_codBarras}, Nombre genérico: {m.med_nombreGen}, "
                f"Nombre comercial: {m.med_nombreComer}, Laboratorio: {m.med_lab}, "
                f"Origen: {m.med_origen}, Concentración: {m.med_concentracion}, "
                f"Forma farmacéutica: {m.med_formaFarma}, Vía: {m.med_viaAdmi}, "
                f"Lote: {m.med_lote}, Caducidad: {m.med_fechaCad}, "
                f"Fracción: {m.med_fraccion}, Precio: ${m.med_precio}, "
                f"Existencia: {m.med_existencia}, Proveedor ID: {m.prov_id}"
            )
            print("=======================================================================================")
        else:
            print("Medicamento no encontrado")

    except Exception as e:
        print("Error al buscar medicamento")
        print(e)

def actualizar_medicamento():
    try:

        med_id = int(input("ID del medicamento a actualizar: "))
        m = MedicamentoDAO.obtener_por_id(med_id)

        if m:
            m.med_codBarras = input("Nuevo código de barras: ")
            m.med_nombreGen = input("Nuevo nombre genérico: ")
            m.med_nombreComer = input("Nuevo nombre comercial: ")
            m.med_lab = input("Nuevo laboratorio: ")
            m.med_origen = input("Nuevo origen: ")
            m.med_concentracion = input("Nueva concentración: ")
            m.med_formaFarma = input("Nueva forma farmacéutica: ")
            m.med_viaAdmi = input("Nueva vía de administración: ")
            m.med_lote = input("Nuevo lote: ")
            m.med_fechaCad = input("Nueva fecha de caducidad (YYYY-MM-DD): ")
            m.med_fraccion = input("Nueva fracción: ")
            m.med_precio = float(input("Nuevo precio: "))
            m.med_existencia = int(input("Nueva existencia: "))
            m.prov_id = int(input("Nuevo ID de proveedor: "))

            MedicamentoDAO.actualizar(m)
            print("Medicamento actualizado con éxito")
        else:
            print("Medicamento no encontrado")

    except Exception as e:
        print("Error al actualizar medicamento")
        print(e)

def eliminar_medicamento():
    try:
        med_id = int(input("ID del medicamento a eliminar: "))
        m = MedicamentoDAO.obtener_por_id(med_id)

        if m:
            MedicamentoDAO.eliminar(med_id)
            print("Medicamento eliminado con éxito")
        else:
            print("Medicamento no encontrado")

    except Exception as e:
        print("Error al eliminar medicamento")
        print(e)

# FUNCIONES DE PRODUCTO
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

# FUNCIONES DE CATEGORIA
def crear_categoria():
    try:

        cat_nombre = input("Nombre de la categoria: ")
        cat_descripcion = input("Descripcion: ")

        nueva = Categoria(cat_nombre, cat_descripcion)
        CategoriaDAO.crear(nueva)
        print("Categoria creada con exito")

    except Exception as e:
        print("Error al crear categoria")
        print(e)


def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver proveedores")
    print("2.- Crear proveedor")
    print("3.- Actualizar proveedor")
    print("4.- Eliminar proveedor")
    print("5.- Insertar medicamento")
    print("6.- Ver medicamentos")
    print("7.- Actualizar medicamento")
    print("8.- Eliminar medicamento")
    print("9.- Ver productos")
    print("10.- Crear producto")
    print("11.- Actualizar producto")
    print("12.- Eliminar producto")

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
        case 5:
            crear_medicamento()
        case 6:
            ver_medicamentos()
        case 7:
            actualizar_medicamento()
        case 8:
            eliminar_medicamento()
        case 9:
            ver_productos()
        case 10:
            crear_producto()
        case 11:
            actualizar_producto()
        case 12:
            eliminar_producto()

if __name__ == "__main__":
    main()