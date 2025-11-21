from dataclasses import dataclass, field
from datetime import datetime
from enums.tipo_usuario_enum import TipoUsuarioEnum
from enums.modalidad_enum import ModalidadEnum
from bson import ObjectId

@dataclass
class Entrevista:
    collection_name = "entrevistas"
    neo_label = "Entrevista"

    # --- Campos obligatorios ---
    id_entrevista: str
    id_busqueda: str           
    entrevistador_email: str   
    entrevistado_email: str    
    fecha_entrevista: datetime
    tipo: ModalidadEnum                  

    # --- Campos por defecto ---
    _id: ObjectId = None
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)

    # --- Métodos de conversión ---
    def to_mongo_document(self):
        return {
            "id_entrevista": self.id_entrevista,
            "id_busqueda": self.id_busqueda,
            "entrevistador_email": self.entrevistador_email,
            "entrevistado_email": self.entrevistado_email,
            "fecha_entrevista": self.fecha_entrevista.isoformat(),
            "tipo": self.tipo.value,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }

    def to_dict(self):
        return self.to_mongo_document()

    def get_neo4j_key(self):
        return "id_entrevista"

    def to_neo4j_node(self):
        return {
            "id_entrevista": self.id_entrevista,
            "id_busqueda": self.id_busqueda,
            "entrevistador_email": self.entrevistador_email,
            "entrevistado_email": self.entrevistado_email,
            "fecha_entrevista": str(self.fecha_entrevista),
            "tipo": self.tipo.value,
            "fecha_creacion": str(self.fecha_creacion)
        }