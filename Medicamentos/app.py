from dao.medicamento_dao import MedicamentoDAO
from models.medicamento import Medicamento

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

def main():
    print("==== PHARMASTOCK ==== ") 
    print("Menu de opciones: ")
    print("1.- Ver medicamentos")
    print("2.- Crear medicamento")
    print("3.- Actualizar medicamento")
    print("4.- Eliminar medicamento")
    
    opc = int(input("Selecciona una opcion: "))

    match opc:
        case 1:
            ver_medicamentos()
        case 2:
            crear_medicamento()
        case 3:
            actualizar_medicamento()
        case 4:
            eliminar_medicamento()

if __name__ == "__main__":
    main()

