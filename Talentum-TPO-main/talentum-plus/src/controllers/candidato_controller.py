from config.mongo_connection import get_mongo_client
from models.candidato import Candidato

db = get_mongo_client()

def crear_candidato(nombre, apellido, email, skills, experiencia):
    candidato = Candidato(nombre, apellido, email, skills, experiencia)
    db.candidatos.insert_one(candidato.to_dict())
    print(f"Candidato {nombre} {apellido} creado exitosamente.")