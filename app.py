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

def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver proveedores")
    print("2.- Crear proveedor")

    
    opc = int(input("Selecciona una opcion: "))

    match opc:
        case 1:
            ver_proveedores()
        case 2:
            crear_proveedor()

if __name__ == "__main__":
    main()