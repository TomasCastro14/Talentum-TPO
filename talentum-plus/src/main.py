from config.mongo_connection import get_mongo_client
from controllers.candidato_controller import crear_candidato

def start_application():
    print("Iniciando Talentum Plus")
    print("Cargando módulos...")
    print()

    db = get_mongo_client()
    print("✅ Conectado a MongoDB")
    print()

if __name__ == "__main__":
    start_application()
    
    # Crear un nuevo candidato
    print("Hola")
    # crear_candidato("Cosmic", "Ray", "comsicray@tralentum.com", ["Python", "Data Analysis"], ["3 years at DataCorp"])
    crear_candidato("Kiro", "Laurent", "kiro@talentium.com", ["JavaScript", "React"], ["2 years at WebSolutions"])

