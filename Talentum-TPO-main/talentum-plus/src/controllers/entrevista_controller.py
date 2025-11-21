from datetime import datetime
from models.entrevista import Entrevista


class EntrevistaController:

    # ==========================
    #        CREAR
    # ==========================

    @staticmethod
    def crear_entrevista_input(mongo_controller, neo_controller=None):
        """
        Pide por consola los datos para crear una entrevista
        y delega en crear_entrevista().
        """
        print("\n=== Crear nueva entrevista ===")
        id_entrevista = input("ID de la entrevista: ").strip()
        id_busqueda = input("ID de la búsqueda asociada (id_procedimiento): ").strip()
        entrevistador = input("Email del entrevistador (reclutador): ").strip().lower()
        entrevistado = input("Email del entrevistado (candidato): ").strip().lower()

        fecha_str = input(
            "Fecha y hora de la entrevista (YYYY-MM-DD HH:MM): "
        ).strip()
        try:
            fecha_entrevista = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print("[!] Formato de fecha inválido. Se cancela la creación.")
            return None

        tipo = input("Tipo de entrevista (presencial / virtual): ").strip().lower()

        return EntrevistaController.crear_entrevista(
            mongo_controller=mongo_controller,
            neo_controller=neo_controller,
            id_entrevista=id_entrevista,
            busqueda=id_busqueda,
            entrevistador=entrevistador,
            entrevistado=entrevistado,
            fecha_entrevista=fecha_entrevista,
            tipo=tipo,
        )

    @staticmethod
    def crear_entrevista(
        mongo_controller,
        neo_controller,
        id_entrevista,
        busqueda,
        entrevistador,
        entrevistado,
        fecha_entrevista,
        tipo,
    ):
        """
        Crea una Entrevista, la guarda en Mongo
        y, si hay neo_controller, la refleja en Neo4j.
        """
        entrevista = Entrevista(
            id_entrevista=id_entrevista,
            busqueda=busqueda,
            entrevistador=entrevistador,
            entrevistado=entrevistado,
            fecha_entrevista=fecha_entrevista,
            tipo=tipo,
        )

        # 1) Guardar en Mongo
        mongo_controller.insertar_documento(entrevista)
        print(f"[+] Entrevista {id_entrevista} creada en MongoDB.")

        # 2) Guardar en Neo4j (nodo + relaciones básicas)
        if neo_controller is not None:
            try:
                neo_controller.crear_nodo_entrevista(entrevista.to_dict())
                neo_controller.relacionar_entrevista_con_busqueda_y_usuarios(
                    id_entrevista=entrevista.id_entrevista,
                    id_busqueda=entrevista.busqueda,
                    entrevistador=entrevista.entrevistador,
                    entrevistado=entrevista.entrevistado,
                )
                print("[+] Entrevista creada y relacionada en Neo4j.")
            except Exception as e:
                print(f"[!] Error al crear entrevista en Neo4j: {e}")

        return entrevista

    # ==========================
    #   CAMBIAR FECHA
    # ==========================

    @staticmethod
    def cambiar_fecha_entrevista(
        mongo_controller,
        neo_controller,
        id_entrevista,
        nueva_fecha,
    ):
        """
        Cambia la fecha de la entrevista en Mongo y en Neo4j.
        nueva_fecha puede ser datetime o string 'YYYY-MM-DD HH:MM'.
        """
        if isinstance(nueva_fecha, str):
            try:
                nueva_fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d %H:%M")
            except ValueError:
                print("[!] Formato de fecha inválido. No se actualiza.")
                return False

        fecha_iso = nueva_fecha.isoformat()

        # 1) Actualizar en Mongo
        mongo_controller.actualizar_documento(
            "entrevistas",
            {"id_entrevista": id_entrevista},
            {"fecha_entrevista": fecha_iso},
        )
        print(f"[+] Fecha de entrevista actualizada en MongoDB ({id_entrevista}).")

        # 2) Actualizar en Neo4j
        if neo_controller is not None:
            try:
                neo_controller.actualizar_fecha_entrevista(id_entrevista, fecha_iso)
                print("[+] Fecha de entrevista actualizada en Neo4j.")
            except Exception as e:
                print(f"[!] Error al actualizar fecha en Neo4j: {e}")

        return True

    # ==========================
    #  CAMBIAR ENTREVISTADOR
    # ==========================

    @staticmethod
    def cambiar_entrevistador(
        mongo_controller,
        neo_controller,
        id_entrevista,
        nuevo_entrevistador,
    ):
        """
        Cambia el entrevistador (reclutador) de una entrevista
        en Mongo y en Neo4j.
        """
        nuevo_entrevistador = nuevo_entrevistador.strip().lower()

        # 1) Actualizar en Mongo
        mongo_controller.actualizar_documento(
            "entrevistas",
            {"id_entrevista": id_entrevista},
            {"entrevistador": nuevo_entrevistador},
        )
        print(f"[+] Entrevistador actualizado en MongoDB ({id_entrevista}).")

        # 2) Actualizar en Neo4j
        if neo_controller is not None:
            try:
                neo_controller.actualizar_entrevistador_entrevista(
                    id_entrevista, nuevo_entrevistador
                )
                print("[+] Entrevistador actualizado en Neo4j.")
            except Exception as e:
                print(f"[!] Error al actualizar entrevistador en Neo4j: {e}")

        return True