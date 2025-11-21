from models.empresa import Empresa
from pymongo.errors import DuplicateKeyError

'''
empresa_controller.py puede hacer las siguientes operaciones CRUD con MongoDB:
    - []
'''

class EmpresaController:

    @staticmethod
    def buscar_empresa_matricula(mongodb, matricula):
        """Busca una empresa por su matrícula en la colección 'empresas'."""
        return mongodb["empresas"].find_one({"matricula": matricula})

    @staticmethod
    def crear_empresa_input(mongodb):
        """Solicita datos al usuario para crear una nueva empresa."""

        print("======== Crear Nueva Empresa ========")

        # --- Datos básicos ---
        nombre = input("Ingrese el nombre de la empresa: ")
        anio_fundacion = input("Ingrese el año de fundación: ")
        matricula = input("Ingrese la matrícula: ")

        # Verificamos que la matrícula sea única
        doc = Empresa

        EmpresaController.crear_empresa(mongodb, nombre, anio_fundacion, matricula)

    @staticmethod
    def crear_empresa(mongodb, nombre, anio_fundacion, matricula):
        """Crea una nueva empresa y la guarda en la base colección 'empresas'."""

        # Aseguramos que exista un índice único en el campo 'matricula'
        mongodb["empresas"].create_index("matricula", unique=True)

        nueva_empresa = Empresa(
            nombre=nombre,
            anio_fundacion=anio_fundacion,
            matricula=matricula
        )

        # Insertamos la empresa en la colección 'empresas'
        try:
            mongodb["empresas"].insert_one(nueva_empresa.to_dict())
            print(f"\n[+] Empresa '{nombre}' creada exitosamente.")
        except DuplicateKeyError:
            print(f"\n[!] Error: Ya existe una empresa con la matrícula '{matricula}'.")