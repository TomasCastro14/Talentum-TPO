from models.usuario import Usuario
from enums.genero_enum import GeneroEnum as Genero
from enums.tipo_usuario_enum import TipoUsuarioEnum as TipoUsuario
from enums.estado_cuenta_enum import EstadoCuentaEnum
from datetime import datetime
from pymongo.errors import DuplicateKeyError

"""
user_controller.py puede hacer las siguentes operaciones CRUD con MongoDB:
    - [C] Crear usuario: Crea al usuario y lo guarda en la colección "usuarios".
    - [R] Buscar Usuario: Puede buscar usuarios en la BDD en base a un input.
    - [U] Eliminar usuario: Marca al usuario como "inactivo", cosa de no perder los datos.
"""

class UserController:

    """
    Métodos de Búsqueda
    """

    @staticmethod
    def buscar_usuario_mail(mongodb, email):
        """
        Busca un usuario en la colección 'usuarios' por su email y lo devuelve como un diccionario.
        """
        doc = mongodb["usuarios"].find_one({"email": email})
        return doc

    """
    Métodos de Creación
    """

    @staticmethod
    def crear_usuario_input(mongodb):
        """Recolecta datos desde consola y crea un nuevo usuario en la base de datos."""

        print("\n=== Crear nuevo usuario ===")

        # --- Datos básicos ---
        nombre = input("Nombre: ")
        apellido = input("Apellido: ")
        email = input("Email: ").strip().lower()
        dni = input("DNI: ")

        # --- Género ---
        genero_input = input("Género (M/F/X): ").upper()
        if genero_input == "M":
            genero = Genero.M
        elif genero_input == "F":
            genero = Genero.F
        else:
            genero = Genero.X

        # --- Fecha de nacimiento ---
        fecha_nac_str = input("Fecha de nacimiento (AAAA-MM-DD): ")
        fecha_nacimiento = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()

        # --- Tipo de usuario ---
        print("Tipo de usuario:\n1. Desempleado\n2. Empleado\n3. Reclutador")
        tipo_usuario_input = int(input("Seleccione una opción (1-3): "))
        tipo_usuario = TipoUsuario(tipo_usuario_input)

        # --- Relaciones ---
        experiencia = input("Experiencia (descripción o dejar vacío): ").strip()
        historial_laboral = input("Historial laboral (empresas separadas por comas): ").split(',')
        historial_entrevistas = input("Historial de entrevistas (separadas por comas): ").split(',')

        # Verificamos que el mail del usuario sea único
        doc = UserController.buscar_usuario_mail(mongodb, email)
        while doc:
            print(f"[!] El usuario ya existe.\n")
            email = input("Email: ").strip().lower()
            doc = UserController.buscar_usuario_mail(mongodb, email)

        # Llamamos a la función encargada de crear e insertar el usuario
        UserController.crear_usuario(
            mongodb=mongodb,
            nombre=nombre,
            apellido=apellido,
            email=email,
            dni=dni,
            genero=genero,
            fecha_nacimiento=fecha_nacimiento,
            tipo_usuario=tipo_usuario,
            experiencia=[experiencia] if experiencia else [],
            historial_laboral=historial_laboral,
            historial_entrevistas=historial_entrevistas
        )

    @staticmethod
    def crear_usuario(mongodb, nombre, apellido, email, dni, genero, fecha_nacimiento, tipo_usuario,
                      experiencia=None, historial_laboral=None, historial_entrevistas=None):
        """Crea un usuario y lo guarda en la colección 'usuarios'."""
        
        # Aseguramos que exista un índice único en el campo 'email'
        mongodb["usuarios"].create_index("email", unique=True)

        # Creamos el objeto Usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            dni=dni,
            genero=genero,
            fecha_nacimiento=fecha_nacimiento,
            tipo_usuario=tipo_usuario,
            experiencia=experiencia or [],
            historial_laboral=historial_laboral or [],
            historial_entrevistas=historial_entrevistas or []
        )

        # Insertamos el usuario en la colección 'usuarios'
        try:
            mongodb["usuarios"].insert_one(nuevo_usuario.to_dict())
            print(f"[+] Usuario {nombre} {apellido} creado exitosamente.\n")
        except DuplicateKeyError:
            print(f"[!] El email '{email}' ya está registrado.\n")

    """
    Métodos de Modificación (Update)
    """

    @staticmethod
    def marcar_usuario_inactivo(mongodb, email, pedir_confirmacion=True):
        """
        Manda a buscar a un usuario por el mail. Si lo encuentra, lo trae, y
        """
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            print(f"[!] No se encontró ningún usuario con el email: {email}\n")
            return False
        
        nombre = doc.get("nombre", "<sin nombre>")
        apellido = doc.get("apellido", "<sin apellido>")
        estado_actual = doc.get("activo", "<sin estado>")

        print(f"\n[!] Se encontró al usuario: {nombre} {apellido} - Estado actual: {estado_actual}")

        if pedir_confirmacion:
            confirm = input("¿Está seguro que desea marcar este usuario como INACTIVO? (s/n): ").lower()
            if confirm not in ('s', 'y'):
                print("[*] Operación cancelada.\n")
                return False
        
        fecha_baja = datetime.now().isoformat()
        result = mongodb["usuarios"].update_one(
            {"email": email},
            {"$set": {
                "activo": EstadoCuentaEnum.INACTIVO.value,
                "fecha_baja": fecha_baja
            }}
        )

        if result.matched_count == 0:
            print("[!] No se actualizó: el usuario dejó de existir entre la búsqueda y la actualización.")
            return False

        if result.modified_count == 0:
            print("[!] El usuario ya estaba marcado como INACTIVO.")
            return True  # técnicamente no modificó pero la intención se cumplió

        print(f"[+] Usuario {nombre} {apellido} marcado como INACTIVO correctamente.")
        return True