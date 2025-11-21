from models.busqueda import Busqueda

from models.usuario import Usuario
from models.empresa import Empresa

from enums.tipo_usuario_enum import TipoUsuarioEnum
from enums.modalidad_enum import ModalidadEnum

from datetime import datetime

class BusquedaController:

    """
    Validación
    """
    @staticmethod
    def validar_empresa(mongo_controller, empresa_email):
        empresa_doc = mongo_controller.buscar_documento_mail(Empresa, empresa_email)

        while not empresa_doc:
            print(f"\n[!] No existe una empresa con el email '{empresa_email}'. Por favor, ingrese un email válido.")
            empresa_email = input("Email de la empresa: ")
            empresa_doc = mongo_controller.buscar_documento_mail(Empresa, empresa_email)

        return empresa_email

    @staticmethod
    def validar_reclutador(mongo_controller, reclutador_mail):
        usuario_doc = mongo_controller.buscar_documento_mail(Usuario, reclutador_mail)

        while not usuario_doc or usuario_doc['tipo_usuario'] != TipoUsuarioEnum.RECLUTADOR.name:
            print(f"\n[!] No existe un reclutador con el email '{reclutador_mail}'. Por favor, ingrese un email válido.")
            reclutador_mail = input("Email del reclutador: ")
            usuario_doc = mongo_controller.buscar_documento_mail(Usuario, reclutador_mail)

        return reclutador_mail

    """
    Métodos de creación
    """

    @staticmethod
    def crear_busqueda_input(mongo_controller, neo_controller):
        print("\n=== Crear Nueva Publicación de Búsqueda ===")
        titulo = input("Título de la búsqueda: ")
        descripcion = input("Descripción: ")
        
        # --- Fecha de finalización ---
        fecha_finalizacion_str = input("Fecha de finalización (AAAA-MM-DD): ")
        fecha_finalizacion = datetime.strptime(fecha_finalizacion_str, "%Y-%m-%d").date()
        
        modalidad_str = input("Modalidad (virtual/presencial/mixto): ").strip().upper()
        modalidad = ModalidadEnum[modalidad_str]
        
        ubicacion = input("Ubicación: ").lower().title()
        rubro = input("Rubro: ")
        aptitudes = input("Aptitudes (separar por comas): ").split(",")

        empresa_mail = BusquedaController.validar_empresa(mongo_controller, input("Email de la empresa: "))
        reclutador_mail = BusquedaController.validar_reclutador(mongo_controller, input("Email del reclutador: "))

        nueva_busqueda = Busqueda(
            id_procedimiento=str(datetime.utcnow().timestamp()).replace('.', ''),
            titulo=titulo,
            descripcion=descripcion,
            fecha_finalizacion=fecha_finalizacion,
            modalidad=modalidad,
            ubicacion=ubicacion,
            rubro=rubro,
            aptitudes=aptitudes,
            empresa_email=empresa_mail,
            reclutador_email=reclutador_mail
        )

        # La mandamos a crear_busqueda
        BusquedaController.crear_busqueda(mongo_controller, neo_controller, nueva_busqueda)

    @staticmethod
    def crear_busqueda(mongo_controller, neo_controller, busqueda: Busqueda):
        try:
            mongo_controller.insertar_documento(busqueda)
            neo_controller.crear_nodo(busqueda)

            # Relación: la empresa publica la búsqueda
            neo_controller.crear_relacion(
                obj_origen=busqueda,
                obj_destino_label="Empresa",
                obj_destino_key="email",
                obj_destino_value=busqueda.empresa_email,
                relacion="PUBLICADA_POR"
            )

            # Relación: el reclutador gestiona la búsqueda
            neo_controller.crear_relacion(
                obj_origen=busqueda,
                obj_destino_label="Usuario",
                obj_destino_key="email",
                obj_destino_value=busqueda.reclutador_email,
                relacion="GESTIONADA_POR"
            )

        except Exception as e:
            print(f"[!] Error al insertar la búsqueda en MongoDB: {e}")
            return