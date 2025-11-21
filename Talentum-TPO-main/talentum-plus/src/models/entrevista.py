from datetime import datetime, date

TIPOS_ENTREVISTA_VALIDOS = ("presencial", "virtual")


class Entrevista:
    def __init__(
        self,
        id_entrevista,
        busqueda,
        entrevistador,
        entrevistado,
        fecha_entrevista,
        tipo,
    ):
        self.id_entrevista = id_entrevista
        self.busqueda = busqueda
        self.entrevistador = entrevistador
        self.entrevistado = entrevistado
        self.fecha_entrevista = fecha_entrevista

        tipo_normalizado = tipo.lower()
        if tipo_normalizado not in TIPOS_ENTREVISTA_VALIDOS:
            raise ValueError(
                f"Tipo de entrevista inválido: {tipo}. "
                f"Debe ser uno de {TIPOS_ENTREVISTA_VALIDOS}"
            )
        self.tipo = tipo_normalizado

    def cambiar_fecha(self, nueva_fecha):
        """
        Cambia la fecha de la entrevista.
        `nueva_fecha` puede ser date o datetime.
        """
        self.fecha_entrevista = nueva_fecha

    def cambiar_entrevistador(self, nuevo_entrevistador):
        """
        Cambia el entrevistador (reclutador) asignado.
        """
        self.entrevistador = nuevo_entrevistador

    def to_dict(self):
        """
        Convierte la entrevista a diccionario para guardarla
        en Mongo / Neo4j o enviarla por API.
        """
        if isinstance(self.fecha_entrevista, (datetime, date)):
            fecha_str = self.fecha_entrevista.isoformat()
        else:
            fecha_str = self.fecha_entrevista

        return {
            "id_entrevista": self.id_entrevista,
            "busqueda": self.busqueda,
            "entrevistador": self.entrevistador,
            "entrevistado": self.entrevistado,
            "fecha_entrevista": fecha_str,
            "tipo": self.tipo,
        }

    def __str__(self):
        return (
            f"[{self.id_entrevista}] Entrevista {self.tipo} - "
            f"{self.entrevistado} con {self.entrevistador}"
        )