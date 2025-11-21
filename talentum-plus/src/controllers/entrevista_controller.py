from datetime import datetime

from models.entrevista import Entrevista
from models.usuario import Usuario
from models.empresa import Empresa
from models.busqueda import Busqueda

from enums.tipo_usuario_enum import TipoUsuarioEnum
from enums.modalidad_enum import ModalidadEnum

class EntrevistaController:

    @staticmethod
    def validar_empresa(mongo_controller, empresa_email):
        empresa_doc = mongo_controller.buscar_documento_mail(Empresa, empresa_email)

        while not empresa_doc:
            print(f"\n[!] No existe una empresa con el email '{empresa_email}'. Por favor, ingrese un email válido.")
            empresa_email = input("Email de la empresa: ")
            empresa_doc = mongo_controller.buscar_documento_mail(Empresa, empresa_email)

        return empresa_email
    
    @staticmethod
    def validar_busqueda(neo_controller, empresa_email):
        busquedas = neo_controller.obtener_relaciones(
            label_origen="Empresa",
            key_origen="email",
            value_origen=empresa_email,
            tipo_relacion="PUBLICADA_POR",
            label_destino="Busqueda"
        )

        if not busquedas:
            print("[!] No hay búsquedas activas para esta empresa.")
            return None

        print("\nBúsquedas encontradas:")
        for i, b in enumerate(busquedas):
            print(f"{i+1}. {b['nodo']['titulo']} ({b['nodo']['id_procedimiento']})")

        seleccion = int(input("Seleccione una búsqueda: ")) - 1
        while seleccion < 0 or seleccion >= len(busquedas):
            print("[!] Selección inválida. Intente nuevamente.")
            seleccion = int(input("Seleccione una búsqueda: ")) - 1

        return busquedas[seleccion]["nodo"]
    
    @staticmethod
    def validar_reclutador(mongo_controller, reclutador_mail):
        usuario_doc = mongo_controller.buscar_documento_mail(Usuario, reclutador_mail)

        while not usuario_doc or usuario_doc['tipo_usuario'] != TipoUsuarioEnum.RECLUTADOR.name:
            print(f"\n[!] No existe un reclutador con el email '{reclutador_mail}'. Por favor, ingrese un email válido.")
            reclutador_mail = input("Email del reclutador: ")
            usuario_doc = mongo_controller.buscar_documento_mail(Usuario, reclutador_mail)

        return reclutador_mail
    
    @staticmethod
    def validar_usuario(mongo_controller, usuario_mail):
        usuario_doc = mongo_controller.buscar_documento_mail(Usuario, usuario_mail)

        while not usuario_doc:
            print(f"\n[!] No existe un usuario con el email '{usuario_mail}'. Por favor, ingrese un email válido.")
            usuario_mail = input("Email del reclutador: ")
            usuario_doc = mongo_controller.buscar_documento_mail(Usuario, usuario_mail)

        return usuario_mail

    @staticmethod
    def crear_entrevista_input(mongo_controller, neo_controller):
        print("\n=== Crear Nueva Entrevista ===")

        # --- Selección de Búsqueda ---
        empresa_mail = EntrevistaController.validar_empresa(mongo_controller, input("Email de la empresa: "))
        busqueda_seleccionada = EntrevistaController.validar_busqueda(neo_controller, empresa_mail)
        entrevistador_mail = EntrevistaController.validar_reclutador(mongo_controller, input("Email del entrevistador (reclutador): "))
        entrevistado_mail = EntrevistaController.validar_usuario(mongo_controller, input("Email del entrevistado (candidato): "))

        # --- Datos de la Entrevista ---
        fecha_str = input("Fecha de la entrevista (AAAA-MM-DD HH:MM): ")
        fecha_entrevista = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")

        tipo_str = input("Tipo de entrevista (PRESENCIAL/ VIRTUAL): ").strip().upper()
        tipo = ModalidadEnum[tipo_str]

        nueva_entrevista = Entrevista(
            id_entrevista=str(datetime.utcnow().timestamp()).replace('.', ''),
            id_busqueda=busqueda_seleccionada["id_procedimiento"],
            entrevistador_email=entrevistador_mail,
            entrevistado_email=entrevistado_mail,
            fecha_entrevista=fecha_entrevista,
            tipo=tipo
        )

        EntrevistaController.crear_entrevista(mongo_controller, neo_controller, nueva_entrevista)

    @staticmethod
    def crear_entrevista(mongo_controller, neo_controller, entrevista: Entrevista):
        try:
            mongo_controller.insertar_documento(entrevista)
            neo_controller.crear_nodo(entrevista)
            neo_controller.crear_relacion(
                obj_origen=entrevista,
                obj_destino_label="Busqueda",
                obj_destino_key="id_procedimiento",
                obj_destino_value=entrevista.id_busqueda,
                relacion="PERTENECE_A"
            )
            neo_controller.crear_relacion(
                obj_origen=entrevista,
                obj_destino_label="Usuario",
                obj_destino_key="email",
                obj_destino_value=entrevista.entrevistador_email,
                relacion="ENTREVISTA_REALIZADA_POR"
            )
            neo_controller.crear_relacion(
                obj_origen=entrevista,
                obj_destino_label="Usuario",
                obj_destino_key="email",
                obj_destino_value=entrevista.entrevistado_email,
                relacion="ENTREVISTA_A"
            )
            print("[+] Entrevista creada correctamente.")

        except Exception as e:
            print(f"[!] Error creando la entrevista: {e}")