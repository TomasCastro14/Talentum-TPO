from dataclasses import dataclass, field
from datetime import datetime, date
from enums.modalidad_enum import ModalidadEnum
from bson import ObjectId

@dataclass
class Busqueda:
    collection_name = "busquedas"
    neo_label = "Busqueda"

    # --- Campos SIN default primero ---
    id_procedimiento: str
    titulo: str
    descripcion: str
    fecha_finalizacion: datetime
    modalidad: ModalidadEnum
    ubicacion: str
    rubro: str
    aptitudes: list
    empresa_email: str
    reclutador_email: str

    # --- Campos con valor por defecto después ---
    esta_abierta: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    entrevistas: list = field(default_factory=list)
    _id: ObjectId = None

    def to_mongo_document(self):
        return {
            "id_procedimiento": self.id_procedimiento,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_finalizacion": self.fecha_finalizacion.isoformat(),
            "modalidad": self.modalidad.value,
            "ubicacion": self.ubicacion,
            "rubro": self.rubro,
            "aptitudes": self.aptitudes,
            "empresa_email": self.empresa_email,
            "reclutador_email": self.reclutador_email,
            "entrevistas": self.entrevistas,
            "esta_abierta": self.esta_abierta,
            "fecha_finalizacion": self.fecha_finalizacion.isoformat(),
            "fecha_creacion": self.fecha_creacion
        }
    
    def to_dict(self):
        return self.to_mongo_document()

    def get_neo4j_key(self):
        return "id_procedimiento"

    def to_neo4j_node(self):
        return {
            "id_procedimiento": self.id_procedimiento,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "fecha_finalizacion": str(self.fecha_finalizacion),
            "modalidad": self.modalidad.value,
            "ubicacion": self.ubicacion,
            "rubro": self.rubro,
            "fecha_creacion": str(self.fecha_creacion),
            "esta_abierta": self.esta_abierta
        }