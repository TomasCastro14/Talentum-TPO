from config.database_conection import DatabaseConnections
from controllers.user_controller import UserController

def cargar_modulos():
    print("Iniciando Talentum Plus...\n")
    
    print("[+] Creando objetos...\n")
    database_connections = DatabaseConnections()
    user_controller = UserController()

    print("[0/3] Cargando módulos...")
    mongodb = database_connections.mongo_connection()
    neo4jdb = database_connections.neo4j_connection()
    redisdb = database_connections.redis_connection()

    print()
    return mongodb, neo4jdb, redisdb, user_controller

def mostrar_menu():
    print("=== Menú de Talentum Plus ===")
    print("[1] Crear Usuario")
    print("[2] Eliminar Usuario")
    print("[3] Ver Candidatos")
    print("[0] Salir")
    print("=============================")
    print()

def pausar():
    input("\nPresione ENTER para continuar...")

def start_application():

    mongodb, neo4jdb, redisdb, user_controller = cargar_modulos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "0":
            print("\nSaliendo del sistema... ¡Hasta luego!\n")
            break

        elif opcion == "1":
            print("Opcion 1 - Crear Usuario\n")
            user_controller.crear_usuario_input(mongodb)

        elif opcion == "2":
            print("Opcion 2 - Eliminar Usuario\n")
            UserController.marcar_usuario_inactivo(mongodb, input("Ingrese el email del usuario a eliminar: ").strip().lower())

        elif opcion == "3":
            print("Opcion 3")

        else:
            print("\n[!] Opción inválida. Intente nuevamente.\n")

        pausar()

if __name__ == "__main__":
    start_application()

