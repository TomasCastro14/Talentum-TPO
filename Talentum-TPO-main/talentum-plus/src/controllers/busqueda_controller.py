from datetime import datetime, date
from pymongo.errors import DuplicateKeyError

from models.busqueda import Busqueda


class BusquedaController:
    """
    busqueda_controller.py puede hacer las siguientes operaciones:
        - [C] Crear búsqueda (por input o por parámetros).
        - [R] Buscar búsqueda por id_procedimiento.
        - [U] Modificar campos clave: reclutador, fecha de finalización, estado (abrir/cerrar).
        - [U] Agregar postulantes (usuarios) a una búsqueda.
        - [R] Listar búsquedas abiertas / por empresa.
    """

    # ==========================
    #   Helpers internos
    # ==========================

    @staticmethod
    def _construir_busqueda_desde_doc(doc: dict) -> Busqueda:
        """
        Convierte un dict de Mongo en un objeto Busqueda.
        """
        fecha_valor = doc.get("fecha_finalizacion")
        fecha_finalizacion = None

        if isinstance(fecha_valor, date):
            fecha_finalizacion = fecha_valor
        elif isinstance(fecha_valor, str) and fecha_valor.strip():
            try:
                # espera formato ISO 'YYYY-MM-DD'
                fecha_finalizacion = datetime.fromisoformat(fecha_valor).date()
            except ValueError:
                # si no lo puede parsear, la deja en None
                fecha_finalizacion = None

        return Busqueda(
            id_procedimiento=doc["id_procedimiento"],
            titulo=doc.get("titulo"),
            descripcion=doc.get("descripcion"),
            fecha_finalizacion=fecha_finalizacion,
            modalidad_puesto=doc.get("modalidad_puesto"),
            ubicacion_oficina=doc.get("ubicacion_oficina"),
            rubro=doc.get("rubro"),
            empresa=doc.get("empresa"),
            reclutador=doc.get("reclutador"),
            aptitudes=doc.get("aptitudes", []),
            entrevistas=doc.get("entrevistas", []),
            usuarios=doc.get("usuarios", []),
            esta_abierta=doc.get("esta_abierta", True),
        )

    @staticmethod
    def _coleccion(mongo_controller):
        """
        Devuelve la colección de Mongo que guarda las búsquedas.
        """
        return mongo_controller.driver["busquedas"]

    # ==========================
    #       Búsquedas (R)
    # ==========================

    @staticmethod
    def buscar_por_id(mongo_controller, id_procedimiento: str):
        """
        Busca una búsqueda en Mongo por id_procedimiento y devuelve el documento (dict).
        """
        col = BusquedaController._coleccion(mongo_controller)
        doc = col.find_one({"id_procedimiento": id_procedimiento})

        if not doc:
            print(f"[-] No se encontró búsqueda con id_procedimiento = {id_procedimiento}")
            return None

        print(f"[+] Búsqueda encontrada: {doc.get('titulo', '<sin título>')}")
        return doc

    # ==========================
    #       Crear (C)
    # ==========================

    @staticmethod
    def crear_busqueda_input(mongo_controller, neo_controller=None):
        """
        Pide por consola los datos y crea una Busqueda.
        Pensado para ser llamado desde un menú.
        """
        print("\n=== Crear nueva búsqueda ===")
        id_procedimiento = input("ID del procedimiento: ").strip()
        titulo = input("Título del puesto: ").strip()
        descripcion = input("Descripción del puesto: ").strip()

        fecha_str = input("Fecha de finalización (YYYY-MM-DD, vacío si no aplica): ").strip()
        if fecha_str:
            try:
                fecha_finalizacion = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                print("[!] Formato de fecha inválido, se guarda sin fecha de finalización.")
                fecha_finalizacion = None
        else:
            fecha_finalizacion = None

        modalidad_puesto = input("Modalidad del puesto (presencial/híbrido/remoto): ").strip()
        ubicacion_oficina = input("Ubicación de la oficina: ").strip()
        rubro = input("Rubro de la empresa/puesto: ").strip()

        empresa = input("Matrícula de la empresa que publica la búsqueda: ").strip()
        reclutador = input("Email del reclutador responsable: ").strip().lower()

        aptitudes_input = input(
            "Aptitudes requeridas (separadas por coma, ej: Python,Trabajo en equipo): "
        ).strip()
        aptitudes = [a.strip() for a in aptitudes_input.split(",") if a.strip()] if aptitudes_input else []

        usuarios_input = input(
            "Postulantes iniciales (emails separados por coma, dejar vacío si no hay): "
        ).strip()
        usuarios = [u.strip().lower() for u in usuarios_input.split(",") if u.strip()] if usuarios_input else []

        esta_abierta_str = input("¿Búsqueda abierta? (s/n, por defecto s): ").strip().lower()
        esta_abierta = esta_abierta_str != "n"

        return BusquedaController.crear_busqueda(
            mongo_controller=mongo_controller,
            neo_controller=neo_controller,
            id_procedimiento=id_procedimiento,
            titulo=titulo,
            descripcion=descripcion,
            fecha_finalizacion=fecha_finalizacion,
            modalidad_puesto=modalidad_puesto,
            ubicacion_oficina=ubicacion_oficina,
            rubro=rubro,
            empresa=empresa,
            reclutador=reclutador,
            aptitudes=aptitudes,
            usuarios=usuarios,
            esta_abierta=esta_abierta,
        )

    @staticmethod
    def crear_busqueda(
        mongo_controller,
        neo_controller,
        id_procedimiento,
        titulo,
        descripcion,
        fecha_finalizacion,
        modalidad_puesto,
        ubicacion_oficina,
        rubro,
        empresa,
        reclutador,
        aptitudes=None,
        usuarios=None,
        esta_abierta=True,
    ):
        """
        Crea una Busqueda y la guarda en Mongo.
        Si hay un neo_controller, también crea el nodo y las relaciones en Neo4j.
        """
        aptitudes = aptitudes or []
        usuarios = usuarios or []

        nueva_busqueda = Busqueda(
            id_procedimiento=id_procedimiento,
            titulo=titulo,
            descripcion=descripcion,
            fecha_finalizacion=fecha_finalizacion,
            modalidad_puesto=modalidad_puesto,
            ubicacion_oficina=ubicacion_oficina,
            rubro=rubro,
            empresa=empresa,
            reclutador=reclutador,
            aptitudes=aptitudes,
            entrevistas=[],
            usuarios=usuarios,
            esta_abierta=esta_abierta,
        )

        col = BusquedaController._coleccion(mongo_controller)

        # Índice único en id_procedimiento
        try:
            col.create_index("id_procedimiento", unique=True)
        except Exception as e:
            print(f"[!] Error al crear índice único en id_procedimiento: {e}")

        # Insertar en Mongo
        try:
            mongo_controller.insertar_documento(nueva_busqueda)
        except DuplicateKeyError:
            print(f"[!] Ya existe una búsqueda con id_procedimiento '{id_procedimiento}'.")
            return None

        print(f"[+] Búsqueda '{titulo}' creada correctamente en MongoDB.")

        # Crear nodo y relaciones en Neo4j
        if neo_controller is not None:
            try:
                # Estos métodos los definimos en el NeoController extendido
                neo_controller.crear_nodo_busqueda(nueva_busqueda)
                neo_controller.relacionar_busqueda_completa(nueva_busqueda)
                print("[+] Búsqueda creada y relacionada en Neo4j.")
            except Exception as e:
                print(f"[!] Error al crear nodos/relaciones de Búsqueda en Neo4j: {e}")

        return nueva_busqueda

    # ==========================
    #   Update: postulantes
    # ==========================

    @staticmethod
    def agregar_postulante(mongo_controller, neo_controller, id_procedimiento, email_usuario):
        """
        Agrega un usuario (por email) a la lista de postulantes de la búsqueda.
        También crea la relación en Neo4j: (Usuario)-[:POSTULO_A]->(Busqueda).
        """
        doc = BusquedaController.buscar_por_id(mongo_controller, id_procedimiento)
        if not doc:
            return False

        usuarios = doc.get("usuarios", [])
        email_usuario = email_usuario.strip().lower()

        if email_usuario in usuarios:
            print(f"[!] El usuario {email_usuario} ya está postulado a la búsqueda.")
            return False

        usuarios.append(email_usuario)

        # Actualizar Mongo
        mongo_controller.actualizar_documento(
            "busquedas",
            {"id_procedimiento": id_procedimiento},
            {"usuarios": usuarios},
        )
        print(f"[+] Usuario {email_usuario} agregado como postulante en MongoDB.")

        # Actualizar Neo4j
        if neo_controller is not None:
            try:
                neo_controller.crear_relacion_usuario_postula_busqueda(
                    email_usuario, id_procedimiento
                )
                print("[+] Relación POSTULO_A creada en Neo4j.")
            except Exception as e:
                print(f"[!] Error al crear relación POSTULO_A en Neo4j: {e}")

        return True

    # ==========================
    #   Update: reclutador
    # ==========================

    @staticmethod
    def cambiar_reclutador(mongo_controller, neo_controller, id_procedimiento, nuevo_reclutador):
        """
        Cambia el reclutador asignado a una búsqueda.
        (En Neo4j podrías agregar un método específico para actualizar la relación.)
        """
        doc = BusquedaController.buscar_por_id(mongo_controller, id_procedimiento)
        if not doc:
            return False

        busqueda = BusquedaController._construir_busqueda_desde_doc(doc)
        busqueda.cambiar_reclutador(nuevo_reclutador)

        mongo_controller.actualizar_documento(
            "busquedas",
            {"id_procedimiento": id_procedimiento},
            {"reclutador": busqueda.reclutador},
        )
        print(f"[+] Reclutador actualizado en MongoDB a {nuevo_reclutador}.")

        # Opcional: actualizar relaciones en Neo4j
        if neo_controller is not None:
            try:
                # Lo más prolijo sería tener un método tipo:
                # neo_controller.actualizar_reclutador_busqueda(id_procedimiento, nuevo_reclutador)
                # Por ahora, al menos podés volver a relacionar todo:
                neo_controller.relacionar_busqueda_completa(busqueda)
                print("[+] Relaciones de reclutador actualizadas en Neo4j (MERGE).")
            except Exception as e:
                print(f"[!] Error al actualizar reclutador en Neo4j: {e}")

        return True

    # ==========================
    #   Update: fecha / estado
    # ==========================

    @staticmethod
    def cambiar_fecha_finalizacion(mongo_controller, id_procedimiento, nueva_fecha: date):
        """
        Actualiza la fecha de finalización de la búsqueda en MongoDB.
        """
        fecha_str = nueva_fecha.isoformat() if isinstance(nueva_fecha, date) else None

        mongo_controller.actualizar_documento(
            "busquedas",
            {"id_procedimiento": id_procedimiento},
            {"fecha_finalizacion": fecha_str},
        )
        print(f"[+] Fecha de finalización actualizada a {fecha_str}.")

    @staticmethod
    def cerrar_busqueda(mongo_controller, id_procedimiento):
        """
        Marca una búsqueda como cerrada.
        """
        mongo_controller.actualizar_documento(
            "busquedas",
            {"id_procedimiento": id_procedimiento},
            {"esta_abierta": False},
        )
        print(f"[+] Búsqueda {id_procedimiento} marcada como CERRADA.")

    @staticmethod
    def abrir_busqueda(mongo_controller, id_procedimiento):
        """
        Marca una búsqueda como abierta.
        """
        mongo_controller.actualizar_documento(
            "busquedas",
            {"id_procedimiento": id_procedimiento},
            {"esta_abierta": True},
        )
        print(f"[+] Búsqueda {id_procedimiento} marcada como ABIERTA.")

    # ==========================
    #       Listados (R)
    # ==========================

    @staticmethod
    def listar_busquedas_abiertas(mongo_controller):
        """
        Lista por consola todas las búsquedas abiertas.
        """
        col = BusquedaController._coleccion(mongo_controller)
        cursor = col.find({"esta_abierta": True})

        print("\n=== Búsquedas abiertas ===")
        for doc in cursor:
            print(
                f"- [{doc.get('id_procedimiento')}] {doc.get('titulo')} "
                f"({doc.get('ubicacion_oficina', '-')})"
            )

    @staticmethod
    def listar_busquedas_por_empresa(mongo_controller, matricula_empresa):
        """
        Lista las búsquedas asociadas a una empresa (por matrícula).
        """
        col = BusquedaController._coleccion(mongo_controller)
        cursor = col.find({"empresa": matricula_empresa})

        print(f"\n=== Búsquedas de la empresa {matricula_empresa} ===")
        for doc in cursor:
            estado = "Abierta" if doc.get("esta_abierta", True) else "Cerrada"
            print(
                f"- [{doc.get('id_procedimiento')}] {doc.get('titulo')} "
                f"- {estado}"
            )