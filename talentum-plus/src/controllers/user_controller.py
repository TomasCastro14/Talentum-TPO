from controllers.neo4j_controller import NeoController
from controllers.mongo_controller import MongoController
from models.usuario import Usuario
from enums.genero_enum import GeneroEnum as Genero
from enums.tipo_usuario_enum import TipoUsuarioEnum as TipoUsuario
from enums.estado_cuenta_enum import EstadoCuentaEnum
from datetime import date, datetime
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
    def buscar_usuario_mail(mongo_controller, email):
        """
        Busca un usuario en la colección 'usuarios' por su email y lo devuelve como un diccionario.
        """
        doc = mongo_controller.buscar_documento_mail(Usuario, email)

        if not doc:
            print(f"[!] No se encontró ningún usuario en MongoDB con el email: {email}\n")
            return None
        
        return doc
    
    @staticmethod
    def validar_usuario(mongo_controller, usuario_mail):
        usuario_doc = mongo_controller.buscar_documento_mail(Usuario, usuario_mail)

        while not usuario_doc:
            print(f"\n[!] No existe un usuario con el email '{usuario_mail}'. Por favor, ingrese un email válido.")
            usuario_mail = input("Email del reclutador: ")
            usuario_doc = mongo_controller.buscar_documento_mail(Usuario, usuario_mail)

        return usuario_mail
    
    @staticmethod
    def seleccionar_postulacion(postulaciones):
        print("\n=== Seleccione la postulación que desea iniciar ===")
        for idx, post in enumerate(postulaciones, start=1):
            print(f"{idx}. {post['titulo']} ({post['id_procedimiento']}) - Rubro: {post['rubro']}, Modalidad: {post['modalidad']}")
        while True:
            try:
                seleccion = int(input("Ingrese el número de la postulación: "))
                if 1 <= seleccion <= len(postulaciones):
                    return postulaciones[seleccion - 1]
                else:
                    print(f"[!] Ingrese un número entre 1 y {len(postulaciones)}.")
            except ValueError:
                print("[!] Ingrese un número válido.")

    @staticmethod
    def buscar_usuario_neo4j(neo4jdb, email):
        query = "MATCH (u:Usuario {email: $email}) RETURN u"
        with neo4jdb.session(database="neo4j") as session:
            result = session.run(query, {"email": email}).single()
            if result:
                return result["u"]
            else:
                print(f"[!] No se encontró ningún usuario en Neo4J con el email: {email}\n")
                return None

    """
    Métodos de Creación
    """

    @staticmethod
    def crear_usuario_input(mongo_controller, neo_controller):
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
        doc = UserController.buscar_usuario_mail(mongo_controller, email)
        while doc:
            print(f"[!] El usuario ya existe.\n")
            email = input("Email: ").strip().lower()
            doc = UserController.buscar_usuario_mail(mongo_controller, email)

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

        # Llamamos a la función encargada de crear e insertar el usuario
        UserController.crear_usuario(mongo_controller, neo_controller, nuevo_usuario)

    @staticmethod
    def crear_usuario(mongo_controller, neo_controller, nuevo_usuario):
        """Crea un usuario y lo guarda en la colección 'usuarios'."""

        # Aseguramos que exista un índice único en el campo 'email'
        try:
            mongo_controller.driver[Usuario.collection_name].create_index("email", unique=True)
        except Exception as e:
            print(f"[!] Error al crear índice único en email: {e}")

        # Insertamos el usuario en la colección 'usuarios'
        try:
            mongo_controller.insertar_documento(nuevo_usuario)
            neo_controller.crear_nodo(nuevo_usuario)
        except DuplicateKeyError:
            print(f"[!] El email '{nuevo_usuario.email}' ya está registrado.\n")

        print(f"[+] Usuario {nuevo_usuario.nombre} {nuevo_usuario.apellido} creado exitosamente.\n")

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
    def cambiar_nombre_usuario(mongo_controller, neo_controller):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongo_controller, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')} {doc.get('apellido', '<sin apellido>')}\n")
        nuevo_nombre = input("Ingrese el nuevo nombre: ").strip().lower().title()
        if not UserController.confirmar_accion("Desea continuar con el cambio de nombre", doc.get('nombre', '<sin nombre>'), nuevo_nombre):
            return False

        # Neo4J
        mongo_controller.actualizar_documento(collection_name="usuarios", filtro={"email": email}, campos={"nombre": nuevo_nombre.value})
        neo_controller.actualizar_usuario(email, {"nombre": nuevo_nombre})


        print(f"[+] Nombre cambiado exitosamente a {nuevo_nombre}.")

    @staticmethod
    def cambiar_apellido_usuario(mongo_controller, neo_controller):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongo_controller, email)
        if not doc:
            return False
        
        print(f"\n[!] Se encontró al usuario: {doc.get('nombre', '<sin nombre>')} {doc.get('apellido', '<sin apellido>')}\n")
        nuevo_apellido = input("Ingrese el nuevo apellido: ").strip().lower().title()   
        if not UserController.confirmar_accion("Desea continuar con el cambio de apellido", doc.get('apellido', '<sin nombre>'), nuevo_apellido):
            return False

        # Actualizamos en Neo4J
        mongo_controller.actualizar_documento(collection_name="usuarios", filtro={"email": email}, campos={"apellido": nuevo_apellido.value})
        neo_controller.actualizar_usuario(email, {"apellido": nuevo_apellido})


        print(f"[+] Apellido cambiado exitosamente a {nuevo_apellido}.")

    @staticmethod
    def cambiar_genero_usuario(mongo_controller, neo_controller):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongo_controller, email)
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
        
        # Actualizamos en MongoDB
        # result = mongodb["usuarios"].update_one(
        #    {"email": email},
        #    {"$set": {
        #        "genero": nuevo_genero.value
        #    }}
        #)
        print(f"[+] Actualizado en MongoDB")

        # Actualizamos en las BDD
        mongo_controller.actualizar_documento(collection_name="usuarios", filtro={"email": email}, campos={"genero": nuevo_genero.value})
        neo_controller.actualizar_usuario(email, {"genero": nuevo_genero.value})

        print(f"[+] Género cambiado exitosamente a {nuevo_genero.value}.")

    @staticmethod
    def cambiar_tipo_usuario(mongo_controller, neo_controller):
        email = UserController.email_input()
        doc = UserController.buscar_usuario_mail(mongo_controller, email)
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

        # Neo4J
        mongo_controller.actualizar_documento(collection_name="usuarios", filtro={"email": email}, campos={"tipo_usuario": nuevo_tipo.value})
        neo_controller.actualizar_usuario(email, {"genero": nuevo_tipo.value})

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

    """
    Métodos de Recomendación
    """
    @staticmethod
    def recomendar_postulaciones_rubro(mongo_controller, neo_controller):
        usuario_mail = UserController.validar_usuario(
            mongo_controller,
            input("Email del usuario a recomendar postulaciones: ")
        )
        usuario = UserController.buscar_usuario_mail(mongo_controller, usuario_mail)

        historial = usuario.get("historial_laboral", [])
        if not historial:
            print("[!] El usuario no tiene historial laboral registrado.")
            return []

        recomendaciones = []

        for rubro in historial:  # ahora cada 'rubro' es un string
            if not rubro:
                continue

            postulaciones = neo_controller.buscar_nodos_por_campo(
                label="Busqueda",
                campo="rubro",
                valor=rubro,
                operador="="  # Igualdad exacta
            )
            recomendaciones.extend(postulaciones)

        # Eliminar duplicados por id_procedimiento
        recomendaciones = {p["id_procedimiento"]: p for p in recomendaciones}.values()

        # Mostrar resultados
        print("\n=== Postulaciones recomendadas ===")
        for b in recomendaciones:
            print(f"- {b['titulo']} ({b['id_procedimiento']})")
            #print(f"  Mail de la empresa: {b['empresa_email']}")
            print(f"  Rubro: {b['rubro']}")
            print(f"  Modalidad: {b['modalidad']}")
            print(f"  Descripción: {b['descripcion']}")
            print("==================================\n")
    
    @staticmethod
    def recomendar_postulaciones_ubicacion(mongo_controller, neo_controller):
        ubicacion_usuario = input("Ingrese la ubicación deseada: ").lower().title()

        recomendaciones = []

        # Buscamos las postulaciones que coincidan con la ubicación
        postulaciones = neo_controller.buscar_nodos_por_campo(
            label="Busqueda",
            campo="ubicacion",
            valor=ubicacion_usuario,
            operador="="  # Igualdad exacta
        )
        recomendaciones.extend(postulaciones)

        # Eliminar duplicados por id_procedimiento
        recomendaciones = {p["id_procedimiento"]: p for p in recomendaciones}.values()

        # Mostrar resultados
        print("\n=== Postulaciones recomendadas por ubicación ===")
        for b in recomendaciones:
            print(f"- {b['titulo']} ({b['id_procedimiento']})")
            print(f"  Rubro: {b['rubro']}")
            print(f"  Modalidad: {b['modalidad']}")
            print(f"  Descripción: {b['descripcion']}")
            print("==================================\n")

        return list(recomendaciones)
    
    @staticmethod
    def recomendar_postulaciones_modalidad(mongo_controller, neo_controller):
        modalidad_usuario = input("Ingrese la modalidad deseada (presencial, virtual, mixto): ").lower()

        recomendaciones = []

        # Buscamos las postulaciones que coincidan con la modalidad
        postulaciones = neo_controller.buscar_nodos_por_campo(
            label="Busqueda",
            campo="modalidad",
            valor=modalidad_usuario,
            operador="="  # Igualdad exacta
        )
        recomendaciones.extend(postulaciones)

        # Eliminar duplicados por id_procedimiento
        recomendaciones = {p["id_procedimiento"]: p for p in recomendaciones}.values()

        # Mostrar resultados
        print("\n=== Postulaciones recomendadas por modalidad ===")
        for b in recomendaciones:
            print(f"- {b['titulo']} ({b['id_procedimiento']})")
            print(f"  Rubro: {b['rubro']}")
            print(f"  Modalidad: {b['modalidad']}")
            print(f"  Descripción: {b['descripcion']}")
            print("==================================\n")

        return list(recomendaciones)

    @staticmethod
    def iniciar_postulacion(mongo_controller, neo_controller, postulaciones):
        if not postulaciones:
            print("[!] No hay postulaciones disponibles para iniciar.")
            return

        # --- Validar usuario ---
        usuario_doc = UserController.validar_usuario(
            mongo_controller,
            input("Ingrese su email para iniciar la postulación: ")
        )

        # Reconstruir objeto Usuario desde el documento de Mongo
        usuario = Usuario(
            nombre=usuario_doc["nombre"],
            apellido=usuario_doc["apellido"],
            email=usuario_doc["email"],
            dni=usuario_doc["dni"],
            genero=Genero(usuario_doc["genero"]),
            fecha_nacimiento=date.fromisoformat(usuario_doc["fecha_nacimiento"]),
            tipo_usuario=TipoUsuario[usuario_doc["tipo_usuario"]],
            experiencia=usuario_doc.get("experiencia", []),
            historial_laboral=usuario_doc.get("historial_laboral", []),
            historial_entrevistas=usuario_doc.get("historial_entrevistas", []),
            relaciones=usuario_doc.get("relaciones", [])
        )

        # --- Seleccionar postulación ---
        post_seleccionada = UserController.seleccionar_postulacion(postulaciones)

        # --- Crear relación en Neo4J ---
        try:
            neo_controller.crear_relacion(
                obj_origen=usuario,
                obj_destino_label="Busqueda",
                obj_destino_key="id_procedimiento",
                obj_destino_value=post_seleccionada["id_procedimiento"],
                relacion="POSTULA_A"
            )
            print(f"[+] Postulación iniciada correctamente para {usuario.email} a {post_seleccionada['titulo']}")
        except Exception as e:
            print(f"[!] Error al iniciar la postulación: {e}")
