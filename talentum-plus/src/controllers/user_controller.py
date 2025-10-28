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
    Métodos de Repetición
    """
    @staticmethod
    def confirmar_accion(mensaje, variable_uno, variable_dos):
        """Pide confirmación al usuario para continuar con una acción."""
        print(f"[?] ¿{mensaje}? {variable_uno} -> {variable_dos}")
        confirm = input("\tConfirmar (s/n): ").lower()

        while confirm not in ('s', 'y', 'n'):
            print(f"[!] Respuesta inválida. Por favor ingrese 's' para sí o 'n' para no.")
            print(f"\n[?] ¿{mensaje}? {variable_uno} -> {variable_dos}")
            confirm = input("\tConfirmar (s/n): ").lower()

        match confirm:
            case 's' | 'y':
                return True
            case 'n':
                print("\n[-] Operación cancelada.")
                return False

    """
    Métodos de Búsqueda
    """

    @staticmethod
    def email_input():
        """Pide un email por consola y lo devuelve."""
        email = input("Ingrese el email del usuario: ").strip().lower()

        while not email:
            print("[!] El email no puede estar vacío.")
            email = input("Ingrese el email del usuario: ").strip().lower()

        return email

    @staticmethod
    def buscar_usuario_mail(mongodb, email):
        """
        Busca un usuario en la colección 'usuarios' por su email y lo devuelve como un diccionario.
        """
        doc = mongodb["usuarios"].find_one({"email": email})

        if not doc:
            print(f"[!] No se encontró ningún usuario con el email: {email}\n")
            return False

        return doc

    """
    Métodos de Creación
    """

    @staticmethod
    def crear_usuario_input(mongodb):
        """Recolecta datos desde consola y crea un nuevo usuario en la base de datos."""

        print("\n=== Crear nuevo usuario ===")

        # --- Datos básicos ---
        nombre = input("Nombre: ").lower().title()
        apellido = input("Apellido: ").lower().title()
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
    def cambiar_estado_cuenta(mongodb, pedir_confirmacion=True):
        """
        Este método cambia el estado de la cuenta de un usuario a INACTIVO o ACTIVO, según el actual estado de la cuenta.
        El programa NUNCA elimina usuarios, sino que los marca como inactivos.
        Manda a buscar a un usuario por el mail. Si lo encuentra, lo trae, y
        """
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            return False
        
        nombre = doc.get("nombre", "<sin nombre>")
        apellido = doc.get("apellido", "<sin apellido>")
        estado_cuenta = doc.get("activo", "<sin estado>")

        print(f"\n[!] Se encontró al usuario: {nombre} {apellido} - Estado actual: {estado_cuenta}\n")

        if pedir_confirmacion:
            confirm = input("¿Estás seguro que querés cambiar el estado del usuario? (s/n): ").lower()
            if confirm not in ('s', 'y'):
                return False

        match doc.get("activo", "<sin estado>"):
            case EstadoCuentaEnum.ACTIVO.value:
                fecha_baja = datetime.now().isoformat()
                result = mongodb["usuarios"].update_one(
                    {"email": email},
                    {"$set": {
                        "activo": EstadoCuentaEnum.INACTIVO.value,
                        "fecha_baja": fecha_baja
                    }}
                )
                estado_cuenta = EstadoCuentaEnum.INACTIVO.value

            case EstadoCuentaEnum.INACTIVO.value:
                result = mongodb["usuarios"].update_one(
                    {"email": email},
                    {"$set": {
                        "activo": EstadoCuentaEnum.ACTIVO.value
                    }}
                )
                estado_cuenta = EstadoCuentaEnum.ACTIVO.value

        if result.matched_count == 0:
            print("[!] No se actualizó: el usuario dejó de existir entre la búsqueda y la actualización.")
            return False

        if result.modified_count == 0:
            print("[!] El usuario ya estaba marcado como INACTIVO.")
            return True  # técnicamente no modificó pero la intención se cumplió

        print(f"[+] Usuario {nombre} {apellido} marcado como {estado_cuenta.upper()} correctamente.")
        return True
    
    @staticmethod
    def cambiar_nombre_usuario(mongodb):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')} {doc.get('apellido', '<sin apellido>')}\n")
        nuevo_nombre = input("Ingrese el nuevo nombre: ").strip().lower().title()
        if not UserController.confirmar_accion("Desea continuar con el cambio de nombre", doc.get('nombre', '<sin nombre>'), nuevo_nombre):
            return False
        
        result = mongodb["usuarios"].update_one(
            {"email": email},
            {"$set": {
                "nombre": nuevo_nombre
            }}
        )

        print(f"[+] Nombre cambiado exitosamente a {nuevo_nombre}.")

    @staticmethod
    def cambiar_apellido_usuario(mongodb):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')} {doc.get('apellido', '<sin apellido>')}\n")
        nuevo_apellido = input("Ingrese el nuevo apellido: ").strip().lower().title()   
        if not UserController.confirmar_accion("Desea continuar con el cambio de apellido", doc.get('apellido', '<sin nombre>'), nuevo_apellido):
            return False
        
        result = mongodb["usuarios"].update_one(
            {"email": email},
            {"$set": {
                "apellido": nuevo_apellido
            }}
        )

        print(f"[+] Apellido cambiado exitosamente a {nuevo_apellido}.")

    @staticmethod
    def cambiar_genero_usuario(mongodb):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')}, de género {doc.get('genero', '<sin genero>')}\n")

        genero_input = input("Sleccione su nuevo género (M/F/X): ").upper()
        if genero_input == "M":
            nuevo_genero = Genero.M
        elif genero_input == "F":
            nuevo_genero = Genero.F
        else:
            nuevo_genero = Genero.X

        if not UserController.confirmar_accion("Desea continuar con el cambio de género", doc.get('genero', '<sin nombre>'), nuevo_genero.value):
            return False
        
        result = mongodb["usuarios"].update_one(
            {"email": email},
            {"$set": {
                "genero": nuevo_genero.value
            }}
        )

        print(f"[+] Género cambiado exitosamente a {nuevo_genero.value}.")

    @staticmethod
    def cambiar_tipo_usuario(mongodb):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongodb, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')}, de tipo {doc.get('tipo_usuario', '<sin genero>')}\n")

        print("Seleccione su nueva ocupación:")
        print("1. Desempleado")
        print("2. Empleado")
        print("3. Reclutador")
        tipo_input = int(input("Ocupación (1/2/3): "))

        if tipo_input == 1:
            nuevo_tipo = TipoUsuario.DESEMPLEADO
        elif tipo_input == 2:
            nuevo_tipo = TipoUsuario.EMPLEADO
        elif tipo_input == 3:
            nuevo_tipo == TipoUsuario.RECLUTADOR

        if not UserController.confirmar_accion("Desea continuar con el cambio de apellido", doc.get('tipo_usuario', '<sin nombre>'), nuevo_tipo.name):
            return False
        
        result = mongodb["usuarios"].update_one(
            {"email": email},
            {"$set": {
                "tipo_usuario": nuevo_tipo.value
            }}
        )

        print(f"[+] Tipo de usuario cambiado exitosamente a {nuevo_tipo.name}.")

    @staticmethod
    def agregar_experiencia_usuario(mongodb):
        pass

    @staticmethod
    def agregar_historial_laboral_usuario(mongodb):
        pass

    @staticmethod
    def agregar_historial_entrevistas_usuario(mongodb):
        pass

    @staticmethod
    def agregar_relacion_usuario(mongodb):
        pass