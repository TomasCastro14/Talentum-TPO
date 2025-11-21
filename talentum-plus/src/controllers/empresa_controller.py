
from controllers.mongo_controller import MongoController
from controllers.neo4j_controller import NeoController
from models.empresa import Empresa
from pymongo.errors import DuplicateKeyError
from datetime import datetime

'''
empresa_controller.py puede hacer las siguientes operaciones CRUD con MongoDB:
    - []
'''

class EmpresaController:
    """
    Métodos de creación
    """
    @staticmethod
    def crear_empresa_input(mongo_controller, neo_controller):
        print("\n=== Crear Nueva Empresa ===")
        nombre = input("Nombre de la empresa: ")
        matricula = input("Matrícula: ")
        email = input("Email: ")
        descripcion = input("Descripción: ")
        rubro = input("Rubro (separar por comas): ").split(",")
        pais_origen = input("País de origen: ")

        # --- Fecha de fundación ---
        fecha_fundacion_str = input("Fecha de nacimiento (AAAA-MM-DD): ")
        fecha_fundacion = datetime.strptime(fecha_fundacion_str, "%Y-%m-%d").date()

        # Verificamos que no exista una empresa con el mismo mail
        doc = mongo_controller.buscar_documento_mail(Empresa, email)
        while doc:
            print(f"\n[!] Ya existe una empresa con el email '{email}'. Por favor, ingrese un email diferente.")
            email = input("Email: ")
            doc = mongo_controller.buscar_documento_mail(Empresa, email)
        
        # Crear la nueva empresa
        nueva_empresa = Empresa(
            nombre=nombre,
            matricula=matricula,
            email=email,
            descripcion=descripcion,
            rubro=rubro,
            pais_origen=pais_origen,
            fecha_fundacion=fecha_fundacion
        )

        # La mandamos a crear_emrpesa
        EmpresaController.crear_empresa(mongo_controller, neo_controller, nueva_empresa)
    
    @staticmethod
    def crear_empresa(mongo_controller, neo_controller, empresa: Empresa):

        # Aseguramos que exista un índice único en el campo 'email'
        try:
            mongo_controller.driver[Empresa.collection_name].create_index("email", unique=True)
        except Exception as e:
            print(f"[!] Error al crear índice único en email: {e}")

         # Insertamos el usuario en la colección 'usuarios'
        try:
            mongo_controller.insertar_documento(empresa)
            neo_controller.crear_nodo(empresa)
        except DuplicateKeyError:
            print(f"[!] El email '{empresa.email}' ya está registrado.\n")

        print(f"[+] Usuario {empresa.nombre} creado exitosamente.\n")