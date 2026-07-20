from backend.dao.proveedor_dao import ProveedorDAO
from backend.models.proveedor import Proveedor

from backend.dao.medicamento_dao import MedicamentoDAO
from backend.models.medicamento import Medicamento

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

def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver proveedores")
    print("2.- Crear proveedor")
    print("3.- Actualizar proveedor")
    print("4.- Eliminar proveedor")
    print("5.- Insertar medicamento")

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

if __name__ == "__main__":
    main()